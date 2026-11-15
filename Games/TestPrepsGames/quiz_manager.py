import psycopg2
import random
import re
import unicodedata

from Games.TestPrepsGames.us_geography import US_STATE_CAPITALS


GENERIC_GEO_PREFIXES = ("mount ", "lake ")
GENERIC_GEO_SUFFIXES = (
    " ocean",
    " sea",
    " river",
    " lake",
    " desert",
    " cathedral",
    " museum",
    " tower",
    " bridge",
    " castle",
    " gate",
    " falls",
    " mosque",
    " basilica",
    " palace",
    " abbey",
    " fountain",
    " canal",
    " bridges",
    " bridge",
    " wall",
    " projected",
    " mountains",
    " mountain",
    " range",
)

COUNTRY_ANSWER_ALIASES = (
    ("united states of america", "united states", "usa", "u s a", "us", "u s", "america"),
    ("united arab emirates", "uae", "u a e", "emirates"),
    ("democratic republic of the congo", "democratic republic congo", "dr congo", "drc", "d r c"),
    ("central african republic", "car", "c a r"),
    ("papua new guinea", "png", "p n g"),
    ("new zealand", "nz", "n z"),
    ("saudi arabia", "ksa", "k s a"),
    ("south korea", "republic of korea", "rok", "r o k"),
    ("north korea", "dprk", "d p r k"),
    ("czechia", "czech republic"),
)

GENERAL_ANSWER_ALIASES = (
    ("sao tome", "saint thomas"),
    ("southern ocean", "antarctic ocean", "southern", "antarctic"),
    ("colosseum", "coliseum"),
    ("sofia cathedral", "sofia", "saint sophia cathedral", "saint sophia", "st sophia", "sophia cathedral", "sophia"),
)

US_STATE_ANSWER_ALIASES = tuple(
    (QuizState.state.casefold(), QuizState.abbreviation.casefold())
    for QuizState in US_STATE_CAPITALS
)

class QuizManager:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()
        self.ensure_result_schema()
        self.questions = self.load_questions()
        self.total_questions = len(self.questions)
        self.current_index = 0
        self.score = 0.0
        self.skipped = 0
        self.mode = "multiple_choice"
        self.visual_mode = True  # default to visual phrasing
        self.session_id = None
        self.current_question = None

    def ensure_result_schema(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id SERIAL PRIMARY KEY,
                started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                completed_at TIMESTAMPTZ,
                score DOUBLE PRECISION NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                skipped INTEGER NOT NULL DEFAULT 0,
                mode TEXT NOT NULL DEFAULT 'text'
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
                question_index INTEGER NOT NULL,
                source_table TEXT,
                source_id INTEGER,
                category TEXT,
                prompt TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT,
                status TEXT NOT NULL,
                points DOUBLE PRECISION NOT NULL DEFAULT 0,
                attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        self.conn.commit()

    def set_visual_mode(self, value: bool):
        self.visual_mode = value

    def is_visual_mode(self):
        return self.visual_mode

    def has_column(self, table_name, column_name):
        self.cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = %s
                  AND column_name = %s
            )
            """,
            (table_name, column_name),
        )
        return self.cursor.fetchone()[0]

    def has_table(self, table_name):
        self.cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = %s
            )
            """,
            (table_name,),
        )
        return self.cursor.fetchone()[0]

    def load_questions(self):
        questions = []
        if self.has_table("geography_maps"):
            if self.has_column("geography_maps", "image_data"):
                self.cursor.execute("""
                    SELECT id, country, capital, image_path, direction, image_data
                    FROM geography_maps
                    WHERE direction IN ('country_to_capital', 'capital_to_country')
                      AND (image_data IS NOT NULL OR image_path IS NOT NULL)
                """)
            else:
                self.cursor.execute("""
                    SELECT id, country, capital, image_path, direction, NULL::bytea AS image_data
                    FROM geography_maps
                    WHERE direction IN ('country_to_capital', 'capital_to_country')
                      AND image_path IS NOT NULL
                """)
            rows = self.cursor.fetchall()
            for source_id, country, capital, image_path, direction, image_data in rows:
                if direction == "country_to_capital":
                    if country == "Palestine":
                        visual_prompt = "🗺️ What is the projected capital of this political entity?"
                        text_prompt = "What is the projected capital of Palestine?"
                    else:
                        visual_prompt = "🗺️ What is the capital of this political entity?"
                        text_prompt = f"What is the capital of {country}?"
                    correct_answer = capital
                    answer_kind = "capital"
                    category = "political entities"
                else:
                    if country == "Palestine":
                        visual_prompt = "🗺️ This projected capital belongs to which political entity?"
                        text_prompt = f"{capital} is the projected capital of which political entity?"
                    else:
                        visual_prompt = "🗺️ What political entity has this capital?"
                        text_prompt = f"{capital} is the capital of which political entity?"
                    correct_answer = country
                    answer_kind = "country"
                    category = "political entities"

                questions.append(
                    {
                        "visual_prompt": visual_prompt,
                        "text_prompt": text_prompt,
                        "correct_answer": correct_answer,
                        "image_source": image_data if image_data is not None else image_path,
                        "is_binary_image": image_data is not None,
                        "answer_kind": answer_kind,
                        "category": category,
                        "source_table": "geography_maps",
                        "source_id": source_id,
                    }
                )

        if self.has_table("geography_questions"):
            self.cursor.execute(
                """
                SELECT id, category, prompt, answer, image_path, image_data, answer_kind
                FROM geography_questions
                WHERE image_data IS NOT NULL OR image_path IS NOT NULL
                """
            )
            for source_id, category, prompt, answer, image_path, image_data, answer_kind in self.cursor.fetchall():
                questions.append(
                    {
                        "visual_prompt": prompt,
                        "text_prompt": prompt,
                        "correct_answer": answer,
                        "image_source": image_data if image_data is not None else image_path,
                        "is_binary_image": image_data is not None,
                        "answer_kind": answer_kind,
                        "category": category,
                        "source_table": "geography_questions",
                        "source_id": source_id,
                    }
                )

        random.shuffle(questions)
        return questions

    def start_session(self, questions=None):
        if questions is None:
            questions = self.load_questions()
        self.questions = questions
        random.shuffle(self.questions)
        self.total_questions = len(self.questions)
        self.current_index = 0
        self.score = 0.0
        self.skipped = 0
        self.current_question = None
        self.cursor.execute(
            """
            INSERT INTO quiz_sessions (score, total_questions, skipped, mode)
            VALUES (0, %s, 0, %s)
            RETURNING id
            """,
            (self.total_questions, self.mode),
        )
        self.session_id = self.cursor.fetchone()[0]
        self.conn.commit()

    def finish_session(self):
        if self.session_id is None:
            return
        self.cursor.execute(
            """
            UPDATE quiz_sessions
            SET completed_at = NOW(),
                score = %s,
                total_questions = %s,
                skipped = %s,
                mode = %s
            WHERE id = %s
            """,
            (self.score, self.total_questions, self.skipped, self.mode, self.session_id),
        )
        self.conn.commit()

    def get_next_question(self):
        if self.current_index < self.total_questions:
            row = self.questions[self.current_index]
            self.current_index += 1
            self.current_question = row
            return row
        return None

    def record_attempt(self, question, user_answer, status, points):
        if self.session_id is None:
            return
        prompt_key = "visual_prompt" if self.is_visual_mode() else "text_prompt"
        self.cursor.execute(
            """
            INSERT INTO quiz_attempts (
                session_id,
                question_index,
                source_table,
                source_id,
                category,
                prompt,
                correct_answer,
                user_answer,
                status,
                points
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self.session_id,
                self.current_index,
                question.get("source_table"),
                question.get("source_id"),
                question.get("category"),
                question.get(prompt_key),
                question.get("correct_answer"),
                user_answer,
                status,
                points,
            ),
        )
        self.conn.commit()

    def latest_sessions(self, limit=20):
        self.cursor.execute(
            """
            SELECT id, started_at, completed_at, score, total_questions, skipped
            FROM quiz_sessions
            ORDER BY started_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return self.cursor.fetchall()

    def review_attempts(self, session_id, statuses=("incorrect", "skipped", "timeout")):
        self.cursor.execute(
            """
            SELECT id, question_index, category, prompt, correct_answer, user_answer, status, points
            FROM quiz_attempts
            WHERE session_id = %s
              AND status = ANY(%s)
            ORDER BY question_index
            """,
            (session_id, list(statuses)),
        )
        return self.cursor.fetchall()

    def retry_questions(self, session_id, statuses=("incorrect", "skipped", "timeout")):
        self.cursor.execute(
            """
            SELECT source_table, source_id, prompt, correct_answer
            FROM quiz_attempts
            WHERE session_id = %s
              AND status = ANY(%s)
            ORDER BY question_index
            """,
            (session_id, list(statuses)),
        )
        attempts = self.cursor.fetchall()
        current_questions = self.load_questions()
        by_source = {
            (question.get("source_table"), question.get("source_id")): question
            for question in current_questions
        }
        by_snapshot = {
            (question.get("visual_prompt"), question.get("correct_answer")): question
            for question in current_questions
        }
        retry_questions = []
        seen = set()
        for source_table, source_id, prompt, correct_answer in attempts:
            question = by_source.get((source_table, source_id)) or by_snapshot.get((prompt, correct_answer))
            if not question:
                continue
            key = (question.get("source_table"), question.get("source_id"))
            if key in seen:
                continue
            seen.add(key)
            retry_questions.append(question)
        return retry_questions

    @staticmethod
    def check_answer(user_answer, correct_answer):
        user_answer = user_answer.strip()
        if "," in correct_answer:
            normalized_user_answer = QuizManager.normalize_answer(user_answer)
            return normalized_user_answer in QuizManager.normalize_answer_list(correct_answer)
        return bool(
            QuizManager.answer_aliases(user_answer)
            & QuizManager.answer_aliases(correct_answer)
        )

    @staticmethod
    def normalize_answer(answer):
        answer = unicodedata.normalize("NFKD", answer)
        answer = "".join(char for char in answer if not unicodedata.combining(char))
        return re.sub(r"[^a-z0-9]+", " ", answer.casefold()).strip()

    @staticmethod
    def normalize_answer_list(answer):
        return {
            QuizManager.normalize_answer(part)
            for part in re.split(r",|\band\b|;", answer.casefold())
            if QuizManager.normalize_answer(part)
        }

    @staticmethod
    def answer_aliases(answer):
        normalized_answer = QuizManager.normalize_answer(answer)
        aliases = {normalized_answer}
        aliases.add(re.sub(r"\bs\b", "", normalized_answer).strip())

        for prefix in GENERIC_GEO_PREFIXES:
            if normalized_answer.startswith(prefix):
                aliases.add(normalized_answer[len(prefix):].strip())

        for _ in range(3):
            for candidate in tuple(aliases):
                for suffix in GENERIC_GEO_SUFFIXES:
                    if candidate.endswith(suffix):
                        aliases.add(candidate[: -len(suffix)].strip())

        if normalized_answer.startswith("sea of "):
            aliases.add(normalized_answer.removeprefix("sea of ").strip())
        if " of " in normalized_answer:
            before_of, after_of = normalized_answer.split(" of ", 1)
            aliases.update({before_of.strip(), after_of.strip()})

        if normalized_answer.startswith("saint "):
            aliases.add("st " + normalized_answer.removeprefix("saint ").strip())
        if normalized_answer.startswith("st "):
            aliases.add("saint " + normalized_answer.removeprefix("st ").strip())

        for alias_group in COUNTRY_ANSWER_ALIASES:
            if normalized_answer in alias_group:
                aliases.update(alias_group)

        for alias_group in GENERAL_ANSWER_ALIASES:
            if normalized_answer in alias_group:
                aliases.update(alias_group)

        for alias_group in US_STATE_ANSWER_ALIASES:
            normalized_alias_group = tuple(QuizManager.normalize_answer(alias) for alias in alias_group)
            if normalized_answer in normalized_alias_group:
                aliases.update(normalized_alias_group)

        return {alias for alias in aliases if alias}

    def get_choices(self, correct_answer, answer_kind):
        correct_choice = self.choice_label(correct_answer, answer_kind)
        correct_choices = self.choice_labels(correct_answer, answer_kind)
        pool = sorted(
            {
                self.choice_label(question["correct_answer"], answer_kind)
                for question in self.questions
                if question["answer_kind"] == answer_kind
                and self.choice_label(question["correct_answer"], answer_kind) not in correct_choices
            }
        )
        if len(pool) < 3:
            pool = sorted(
                {
                    self.choice_label(question["correct_answer"], answer_kind)
                    for question in self.questions
                    if self.choice_label(question["correct_answer"], answer_kind) not in correct_choices
                }
            )
        choices = random.sample(pool, min(3, len(pool)))
        choices.append(correct_choice)
        random.shuffle(choices)
        return choices

    @staticmethod
    def choice_label(answer, answer_kind):
        if answer_kind == "country" and "," in answer:
            return answer.split(",", 1)[0].strip()
        return answer

    @staticmethod
    def choice_labels(answer, answer_kind):
        if answer_kind == "country" and "," in answer:
            return {part.strip() for part in answer.split(",")}
        return {answer}

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode