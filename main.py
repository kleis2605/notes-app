from flask import Flask, request, redirect, render_template_string, url_for
import os
import psycopg


app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


# ==========================================================
# DATABASE
# ==========================================================

def get_connection():

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL mangler. "
            "Sæt DATABASE_URL i Render Environment Variables."
        )

    return psycopg.connect(DATABASE_URL)



def create_table():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # Lav notes-tabellen hvis den ikke findes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)


            # Tilføj pinned hvis kolonnen ikke findes endnu
            cursor.execute("""
                ALTER TABLE notes
                ADD COLUMN IF NOT EXISTS pinned BOOLEAN DEFAULT FALSE
            """)


            # Tilføj created_at hvis den ikke findes endnu
            cursor.execute("""
                ALTER TABLE notes
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ
                DEFAULT CURRENT_TIMESTAMP
            """)


            # Tilføj updated_at hvis den ikke findes endnu
            cursor.execute("""
                ALTER TABLE notes
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ
                DEFAULT CURRENT_TIMESTAMP
            """)


        connection.commit()



def load_notes(search=""):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            if search:

                cursor.execute(
                    """
                    SELECT
                        id,
                        text,
                        pinned,
                        created_at,
                        updated_at
                    FROM notes
                    WHERE text ILIKE %s
                    ORDER BY
                        pinned DESC,
                        updated_at DESC,
                        id DESC
                    """,
                    (f"%{search}%",)
                )

            else:

                cursor.execute("""
                    SELECT
                        id,
                        text,
                        pinned,
                        created_at,
                        updated_at
                    FROM notes
                    ORDER BY
                        pinned DESC,
                        updated_at DESC,
                        id DESC
                """)


            return cursor.fetchall()


# ==========================================================
# HTML
# ==========================================================

PAGE = """
<!DOCTYPE html>

<html lang="da">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#0b0b0d"
    >

    <title>Mine Noter</title>


    <style>

        /* ==================================================
           GENERELT
        ================================================== */

        * {
            box-sizing: border-box;
        }


        html {
            scroll-behavior: smooth;
        }


        body {
            margin: 0;

            min-height: 100vh;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;

            background:
                radial-gradient(
                    circle at top,
                    #19191f 0%,
                    #0b0b0d 42%
                );

            background-attachment: fixed;

            color: white;
        }


        button,
        textarea,
        input {
            font-family: inherit;
        }


        button {
            -webkit-tap-highlight-color: transparent;
        }


        .app {
            width: 100%;

            max-width: 720px;

            margin: 0 auto;

            min-height: 100vh;

            padding-bottom: 130px;
        }


        /* ==================================================
           TOPBAR
        ================================================== */

        .topbar {
            position: sticky;

            top: 0;

            z-index: 20;

            padding:
                20px
                18px
                16px;

            background:
                rgba(11, 11, 13, 0.82);

            backdrop-filter:
                blur(20px);

            -webkit-backdrop-filter:
                blur(20px);

            border-bottom:
                1px solid
                rgba(255, 255, 255, 0.06);
        }


        .topbar-row {
            display: flex;

            justify-content: space-between;

            align-items: center;

            gap: 15px;
        }


        .title-area h1 {
            margin: 0;

            font-size: 30px;

            letter-spacing: -1px;
        }


        .title-area p {
            margin:
                4px
                0
                0;

            color: #85858f;

            font-size: 14px;
        }


        .app-badge {
            display: flex;

            align-items: center;

            justify-content: center;

            width: 46px;

            height: 46px;

            border-radius: 15px;

            background:
                linear-gradient(
                    135deg,
                    #ffffff,
                    #bdbdc8
                );

            color: #111;

            font-size: 23px;

            box-shadow:
                0
                8px
                30px
                rgba(255, 255, 255, 0.08);
        }


        /* ==================================================
           SØGNING
        ================================================== */

        .search-area {
            margin-top: 16px;
        }


        .search-form {
            position: relative;

            display: flex;

            align-items: center;
        }


        .search-icon {
            position: absolute;

            left: 15px;

            pointer-events: none;

            font-size: 17px;

            opacity: 0.55;
        }


        .search-input {
            width: 100%;

            padding:
                13px
                44px
                13px
                44px;

            border: 1px solid #29292f;

            border-radius: 15px;

            outline: none;

            background: #17171b;

            color: white;

            font-size: 16px;

            transition:
                border-color 0.15s,
                background 0.15s;
        }


        .search-input:focus {
            border-color: #51515c;

            background: #1b1b20;
        }


        .clear-search {
            position: absolute;

            right: 10px;

            width: 32px;

            height: 32px;

            display: flex;

            justify-content: center;

            align-items: center;

            border: none;

            border-radius: 10px;

            background: #29292f;

            color: #aaa;

            text-decoration: none;

            font-size: 18px;
        }


        /* ==================================================
           SEKTION
        ================================================== */

        .notes {
            padding:
                20px
                18px;
        }


        .section-title {
            display: flex;

            align-items: center;

            gap: 8px;

            margin:
                3px
                2px
                12px;

            color: #85858f;

            font-size: 13px;

            font-weight: 600;

            text-transform: uppercase;

            letter-spacing: 1px;
        }


        /* ==================================================
           NOTE CARD
        ================================================== */

        .note-card {
            position: relative;

            margin-bottom: 13px;

            padding: 18px;

            overflow: hidden;

            background:
                rgba(27, 27, 32, 0.92);

            border:
                1px solid
                rgba(255, 255, 255, 0.07);

            border-radius: 20px;

            box-shadow:
                0
                10px
                30px
                rgba(0, 0, 0, 0.18);

            transition:
                transform 0.15s,
                border-color 0.15s,
                background 0.15s;
        }


        .note-card:hover {
            border-color:
                rgba(255, 255, 255, 0.12);

            background:
                rgba(31, 31, 37, 0.96);
        }


        .note-card:active {
            transform:
                scale(0.995);
        }


        .note-card.pinned {
            border-color:
                rgba(255, 196, 82, 0.25);

            background:
                linear-gradient(
                    145deg,
                    rgba(51, 42, 24, 0.72),
                    rgba(27, 27, 32, 0.96)
                );
        }


        .pin-glow {
            position: absolute;

            width: 100px;

            height: 100px;

            right: -50px;

            top: -50px;

            border-radius: 50%;

            background:
                rgba(255, 196, 82, 0.09);

            filter:
                blur(20px);

            pointer-events: none;
        }


        .note-top {
            display: flex;

            justify-content: space-between;

            align-items: flex-start;

            gap: 12px;
        }


        .note-text {
            flex: 1;

            font-size: 17px;

            line-height: 1.55;

            overflow-wrap: anywhere;

            white-space: pre-wrap;
        }


        /* ==================================================
           PIN KNAP
        ================================================== */

        .pin-form {
            margin: 0;
        }


        .pin-button {
            width: 40px;

            height: 40px;

            flex-shrink: 0;

            display: flex;

            justify-content: center;

            align-items: center;

            border: 1px solid #303036;

            border-radius: 12px;

            background: #222228;

            color: #aaa;

            font-size: 18px;

            cursor: pointer;

            transition:
                transform 0.15s,
                background 0.15s,
                color 0.15s;
        }


        .pin-button.active {
            background:
                rgba(255, 196, 82, 0.14);

            border-color:
                rgba(255, 196, 82, 0.28);

            color: #ffc452;
        }


        .pin-button:active {
            transform:
                scale(0.9);
        }


        /* ==================================================
           NOTE INFO
        ================================================== */

        .note-meta {
            display: flex;

            align-items: center;

            flex-wrap: wrap;

            gap:
                6px
                10px;

            margin-top: 14px;

            color: #72727c;

            font-size: 12px;
        }


        .pinned-label {
            color: #ffc452;

            font-weight: 600;
        }


        /* ==================================================
           NOTE KNAPPER
        ================================================== */

        .note-actions {
            display: flex;

            justify-content: flex-end;

            gap: 8px;

            margin-top: 16px;
        }


        .action-button {
            min-height: 38px;

            padding:
                8px
                14px;

            border: none;

            border-radius: 11px;

            font-size: 14px;

            font-weight: 600;

            cursor: pointer;

            transition:
                transform 0.15s,
                background 0.15s;
        }


        .action-button:active {
            transform:
                scale(0.94);
        }


        .edit-button {
            background: #29292f;

            color: #ddd;
        }


        .edit-button:hover {
            background: #35353d;
        }


        .delete-button {
            background:
                rgba(255, 70, 70, 0.08);

            border:
                1px solid
                rgba(255, 70, 70, 0.16);

            color: #ff6868;
        }


        .delete-button:hover {
            background:
                rgba(255, 70, 70, 0.14);
        }


        /* ==================================================
           PLUS KNAP
        ================================================== */

        .add-button {
            position: fixed;

            right: 24px;

            bottom:
                calc(
                    25px +
                    env(safe-area-inset-bottom)
                );

            width: 66px;

            height: 66px;

            display: flex;

            justify-content: center;

            align-items: center;

            border: none;

            border-radius: 50%;

            background:
                linear-gradient(
                    145deg,
                    #ffffff,
                    #d6d6dc
                );

            color: #111;

            font-size: 36px;

            font-weight: 300;

            cursor: pointer;

            box-shadow:
                0
                16px
                40px
                rgba(0, 0, 0, 0.45);

            z-index: 30;

            transition:
                transform 0.15s;
        }


        .add-button:hover {
            transform:
                scale(1.05);
        }


        .add-button:active {
            transform:
                scale(0.92);
        }


        /* ==================================================
           POPUP BAGGRUND
        ================================================== */

        .modal-background {
            position: fixed;

            inset: 0;

            display: none;

            justify-content: center;

            align-items: center;

            padding: 18px;

            background:
                rgba(0, 0, 0, 0.72);

            backdrop-filter:
                blur(10px);

            -webkit-backdrop-filter:
                blur(10px);

            z-index: 100;
        }


        .modal-background.show {
            display: flex;
        }


        /* ==================================================
           POPUP
        ================================================== */

        .modal {
            width: 100%;

            max-width: 500px;

            padding: 24px;

            background: #1b1b20;

            border:
                1px solid
                rgba(255, 255, 255, 0.08);

            border-radius: 24px;

            box-shadow:
                0
                25px
                70px
                rgba(0, 0, 0, 0.55);

            animation:
                popup 0.18s ease-out;
        }


        @keyframes popup {

            from {
                opacity: 0;

                transform:
                    scale(0.94)
                    translateY(10px);
            }

            to {
                opacity: 1;

                transform:
                    scale(1)
                    translateY(0);
            }

        }


        .modal-icon {
            width: 50px;

            height: 50px;

            display: flex;

            justify-content: center;

            align-items: center;

            margin-bottom: 16px;

            border-radius: 15px;

            background: #28282e;

            font-size: 22px;
        }


        .modal h2 {
            margin:
                0
                0
                7px;

            font-size: 23px;
        }


        .modal-description {
            margin:
                0
                0
                18px;

            color: #888892;

            font-size: 14px;

            line-height: 1.45;
        }


        textarea {
            width: 100%;

            min-height: 160px;

            resize: vertical;

            padding: 15px;

            border: 1px solid #34343c;

            border-radius: 15px;

            outline: none;

            background: #101013;

            color: white;

            font-size: 17px;

            line-height: 1.45;
        }


        textarea:focus {
            border-color: #666674;
        }


        .modal-buttons {
            display: flex;

            gap: 10px;

            margin-top: 15px;
        }


        .modal-buttons button {
            flex: 1;

            min-height: 48px;

            border: none;

            border-radius: 14px;

            font-size: 15px;

            font-weight: 600;

            cursor: pointer;
        }


        .cancel-button {
            background: #29292f;

            color: white;
        }


        .save-button {
            background: white;

            color: #111;
        }


        /* ==================================================
           SLET POPUP
        ================================================== */

        .delete-icon {
            background:
                rgba(255, 70, 70, 0.12);

            color: #ff6262;
        }


        .delete-preview {
            max-height: 130px;

            margin-top: 16px;

            padding: 14px;

            overflow-y: auto;

            background: #101013;

            border: 1px solid #29292f;

            border-radius: 14px;

            color: #ccc;

            line-height: 1.4;

            overflow-wrap: anywhere;
        }


        .delete-confirm {
            background: #dc4141;

            color: white;
        }


        /* ==================================================
           TOM APP
        ================================================== */

        .empty-state {
            padding:
                90px
                20px;

            text-align: center;

            color: #777781;
        }


        .empty-icon {
            width: 68px;

            height: 68px;

            display: flex;

            justify-content: center;

            align-items: center;

            margin:
                0
                auto
                18px;

            border-radius: 22px;

            background: #1b1b20;

            border: 1px solid #29292f;

            font-size: 30px;
        }


        .empty-state h2 {
            margin:
                0
                0
                6px;

            color: #b5b5bd;

            font-size: 20px;
        }


        .empty-state p {
            margin: 0;

            font-size: 14px;
        }


        /* ==================================================
           PC
        ================================================== */

        @media (min-width: 720px) {

            .add-button {
                right:
                    calc(
                        50% - 320px
                    );
            }

        }


        /* ==================================================
           MOBIL
        ================================================== */

        @media (max-width: 520px) {

            .title-area h1 {
                font-size: 27px;
            }


            .app-badge {
                width: 42px;

                height: 42px;

                border-radius: 14px;
            }


            .notes {
                padding:
                    16px
                    14px;
            }


            .topbar {
                padding:
                    18px
                    14px
                    14px;
            }


            .note-card {
                border-radius: 18px;

                padding: 16px;
            }


            .modal-background {
                align-items: flex-end;

                padding: 0;
            }


            .modal {
                max-width: none;

                border-radius:
                    25px
                    25px
                    0
                    0;

                padding:
                    24px
                    20px
                    calc(
                        24px +
                        env(safe-area-inset-bottom)
                    );

                animation:
                    mobilePopup
                    0.22s
                    ease-out;
            }


            @keyframes mobilePopup {

                from {
                    transform:
                        translateY(100%);
                }

                to {
                    transform:
                        translateY(0);
                }

            }

        }

    </style>

</head>


<body>


    <div class="app">


        <!-- =================================================
             TOPBAR
        ================================================== -->

        <div class="topbar">


            <div class="topbar-row">


                <div class="title-area">

                    <h1>
                        Mine noter
                    </h1>

                    <p>

                        {{ total_notes }}

                        {% if total_notes == 1 %}

                            note gemt

                        {% else %}

                            noter gemt

                        {% endif %}

                    </p>

                </div>


                <div class="app-badge">
                    ✦
                </div>


            </div>


            <!-- SØG -->

            <div class="search-area">


                <form
                    class="search-form"
                    method="GET"
                >


                    <span class="search-icon">
                        🔎
                    </span>


                    <input
                        class="search-input"
                        type="text"
                        name="q"
                        value="{{ search }}"
                        placeholder="Søg i dine noter..."
                        autocomplete="off"
                    >


                    {% if search %}

                        <a
                            class="clear-search"
                            href="/"
                        >
                            ×
                        </a>

                    {% endif %}


                </form>


            </div>


        </div>



        <!-- =================================================
             NOTER
        ================================================== -->

        <div class="notes">


            {% if search %}

                <div class="section-title">

                    Søgeresultater

                    ·

                    {{ notes|length }}

                </div>

            {% endif %}



            {% if notes %}


                {% for note in notes %}


                    <div
                        class="
                            note-card
                            {% if note[2] %}
                                pinned
                            {% endif %}
                        "
                        data-id="{{ note[0] }}"
                    >


                        {% if note[2] %}

                            <div class="pin-glow">
                            </div>

                        {% endif %}



                        <div class="note-top">


                            <div class="note-text">

                                {{ note[1] }}

                            </div>



                            <!-- PIN -->

                            <form
                                class="pin-form"
                                method="POST"
                                action="/pin"
                            >


                                <input
                                    type="hidden"
                                    name="id"
                                    value="{{ note[0] }}"
                                >


                                <button
                                    class="
                                        pin-button

                                        {% if note[2] %}
                                            active
                                        {% endif %}
                                    "
                                    type="submit"
                                    title="
                                        {% if note[2] %}
                                            Fjern pin
                                        {% else %}
                                            Pin note
                                        {% endif %}
                                    "
                                >
                                    📌
                                </button>


                            </form>


                        </div>



                        <!-- INFO -->

                        <div class="note-meta">


                            {% if note[2] %}

                                <span class="pinned-label">
                                    📌 Fastgjort
                                </span>

                            {% endif %}


                            <span>

                                🕒

                                {{ note[3].strftime('%d/%m/%Y · %H:%M') }}

                            </span>


                            {% if note[4] and note[3] and note[4] != note[3] %}

                                <span>
                                    · Redigeret
                                </span>

                            {% endif %}


                        </div>



                        <!-- KNAPPER -->

                        <div class="note-actions">


                            <button
                                class="
                                    action-button
                                    edit-button
                                "
                                type="button"
                                onclick="
                                    openEditModal(this)
                                "
                            >
                                ✏️ Rediger
                            </button>


                            <button
                                class="
                                    action-button
                                    delete-button
                                "
                                type="button"
                                onclick="
                                    openDeleteModal(this)
                                "
                            >
                                Slet
                            </button>


                        </div>


                    </div>


                {% endfor %}


            {% else %}


                <div class="empty-state">


                    <div class="empty-icon">

                        {% if search %}

                            🔎

                        {% else %}

                            📝

                        {% endif %}

                    </div>


                    {% if search %}


                        <h2>
                            Ingen resultater
                        </h2>

                        <p>
                            Der blev ikke fundet noget for
                            "{{ search }}"
                        </p>


                    {% else %}


                        <h2>
                            Ingen noter endnu
                        </h2>

                        <p>
                            Tryk på + for at lave din første note
                        </p>


                    {% endif %}


                </div>


            {% endif %}


        </div>


    </div>



    <!-- =====================================================
         PLUS KNAP
    ====================================================== -->

    <button
        class="add-button"
        onclick="openAddModal()"
        aria-label="Ny note"
    >
        +
    </button>



    <!-- =====================================================
         NY NOTE POPUP
    ====================================================== -->

    <div
        class="modal-background"
        id="addModal"
        onclick="
            closeBackground(
                event,
                'addModal'
            )
        "
    >


        <div class="modal">


            <div class="modal-icon">
                ✦
            </div>


            <h2>
                Ny note
            </h2>


            <p class="modal-description">
                Skriv noget du gerne vil huske.
            </p>


            <form method="POST">


                <textarea
                    name="note"
                    id="noteInput"
                    placeholder="Skriv din note..."
                    required
                ></textarea>


                <div class="modal-buttons">


                    <button
                        type="button"
                        class="cancel-button"
                        onclick="
                            closeModal(
                                'addModal'
                            )
                        "
                    >
                        Annuller
                    </button>


                    <button
                        type="submit"
                        class="save-button"
                    >
                        Gem note
                    </button>


                </div>


            </form>


        </div>


    </div>



    <!-- =====================================================
         REDIGER POPUP
    ====================================================== -->

    <div
        class="modal-background"
        id="editModal"
        onclick="
            closeBackground(
                event,
                'editModal'
            )
        "
    >


        <div class="modal">


            <div class="modal-icon">
                ✏️
            </div>


            <h2>
                Rediger note
            </h2>


            <p class="modal-description">
                Opdater teksten og gem ændringen.
            </p>


            <form
                method="POST"
                action="/edit"
            >


                <input
                    type="hidden"
                    name="id"
                    id="editId"
                >


                <textarea
                    name="note"
                    id="editNote"
                    required
                ></textarea>


                <div class="modal-buttons">


                    <button
                        type="button"
                        class="cancel-button"
                        onclick="
                            closeModal(
                                'editModal'
                            )
                        "
                    >
                        Annuller
                    </button>


                    <button
                        type="submit"
                        class="save-button"
                    >
                        Gem ændringer
                    </button>


                </div>


            </form>


        </div>


    </div>



    <!-- =====================================================
         SLET POPUP
    ====================================================== -->

    <div
        class="modal-background"
        id="deleteModal"
        onclick="
            closeBackground(
                event,
                'deleteModal'
            )
        "
    >


        <div class="modal">


            <div class="
                modal-icon
                delete-icon
            ">
                !
            </div>


            <h2>
                Slet note?
            </h2>


            <p class="modal-description">
                Denne handling kan ikke fortrydes.
            </p>


            <div
                class="delete-preview"
                id="deletePreview"
            >
            </div>


            <form
                method="POST"
                action="/delete"
            >


                <input
                    type="hidden"
                    name="id"
                    id="deleteId"
                >


                <div class="modal-buttons">


                    <button
                        type="button"
                        class="cancel-button"
                        onclick="
                            closeModal(
                                'deleteModal'
                            )
                        "
                    >
                        Behold
                    </button>


                    <button
                        type="submit"
                        class="delete-confirm"
                    >
                        Slet note
                    </button>


                </div>


            </form>


        </div>


    </div>



    <!-- =====================================================
         JAVASCRIPT
    ====================================================== -->

    <script>


        // ==================================================
        // NY NOTE
        // ==================================================

        function openAddModal() {

            const modal =
                document.getElementById(
                    "addModal"
                );


            const input =
                document.getElementById(
                    "noteInput"
                );


            modal
                .classList
                .add("show");


            setTimeout(
                function() {

                    input.focus();

                },
                100
            );

        }



        // ==================================================
        // REDIGER
        // ==================================================

        function openEditModal(button) {


            const card =
                button.closest(
                    ".note-card"
                );


            const id =
                card.dataset.id;


            const text =
                card
                    .querySelector(
                        ".note-text"
                    )
                    .textContent
                    .trim();


            document
                .getElementById(
                    "editId"
                )
                .value = id;


            const input =
                document.getElementById(
                    "editNote"
                );


            input.value = text;


            document
                .getElementById(
                    "editModal"
                )
                .classList
                .add("show");


            setTimeout(
                function() {

                    input.focus();


                    input.setSelectionRange(
                        input.value.length,
                        input.value.length
                    );

                },
                100
            );

        }



        // ==================================================
        // SLET
        // ==================================================

        function openDeleteModal(button) {


            const card =
                button.closest(
                    ".note-card"
                );


            const id =
                card.dataset.id;


            const text =
                card
                    .querySelector(
                        ".note-text"
                    )
                    .textContent
                    .trim();


            document
                .getElementById(
                    "deleteId"
                )
                .value = id;


            document
                .getElementById(
                    "deletePreview"
                )
                .textContent = text;


            document
                .getElementById(
                    "deleteModal"
                )
                .classList
                .add("show");

        }



        // ==================================================
        // LUK POPUP
        // ==================================================

        function closeModal(id) {

            document
                .getElementById(id)
                .classList
                .remove("show");

        }



        function closeBackground(
            event,
            id
        ) {

            if (
                event.target.id === id
            ) {

                closeModal(id);

            }

        }



        // ==================================================
        // ESCAPE
        // ==================================================

        document.addEventListener(
            "keydown",
            function(event) {

                if (
                    event.key ===
                    "Escape"
                ) {

                    closeModal(
                        "addModal"
                    );

                    closeModal(
                        "editModal"
                    );

                    closeModal(
                        "deleteModal"
                    );

                }

            }
        );


    </script>


</body>

</html>
"""


# ==========================================================
# FORSIDE + NY NOTE
# ==========================================================

@app.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
def home():


    # ------------------------------------------------------
    # GEM NY NOTE
    # ------------------------------------------------------

    if request.method == "POST":


        note = request.form.get(
            "note",
            ""
        ).strip()


        if note:


            with get_connection() as connection:


                with connection.cursor() as cursor:


                    cursor.execute(
                        """
                        INSERT INTO notes (
                            text,
                            pinned,
                            created_at,
                            updated_at
                        )
                        VALUES (
                            %s,
                            FALSE,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        """,
                        (note,)
                    )


                connection.commit()


        return redirect("/")



    # ------------------------------------------------------
    # SØG
    # ------------------------------------------------------

    search = request.args.get(
        "q",
        ""
    ).strip()


    notes = load_notes(
        search
    )



    # ------------------------------------------------------
    # ANTAL NOTER TOTALT
    # ------------------------------------------------------

    with get_connection() as connection:


        with connection.cursor() as cursor:


            cursor.execute(
                """
                SELECT COUNT(*)
                FROM notes
                """
            )


            total_notes =
                cursor.fetchone()[0]


    return render_template_string(
        PAGE,
        notes=notes,
        search=search,
        total_notes=total_notes
    )


# ==========================================================
# REDIGER NOTE
# ==========================================================

@app.route(
    "/edit",
    methods=["POST"]
)
def edit_note():


    note_id =
        request.form.get(
            "id"
        )


    new_text =
        request.form.get(
            "note",
            ""
        ).strip()


    if (
        note_id
        and
        new_text
    ):


        with get_connection() as connection:


            with connection.cursor() as cursor:


                cursor.execute(
                    """
                    UPDATE notes

                    SET
                        text = %s,
                        updated_at =
                            CURRENT_TIMESTAMP

                    WHERE id = %s
                    """,
                    (
                        new_text,
                        note_id
                    )
                )


            connection.commit()


    return redirect("/")


# ==========================================================
# PIN NOTE
# ==========================================================

@app.route(
    "/pin",
    methods=["POST"]
)
def pin_note():


    note_id =
        request.form.get(
            "id"
        )


    if note_id:


        with get_connection() as connection:


            with connection.cursor() as cursor:


                cursor.execute(
                    """
                    UPDATE notes

                    SET pinned =
                        NOT pinned

                    WHERE id = %s
                    """,
                    (note_id,)
                )


            connection.commit()


    return redirect("/")


# ==========================================================
# SLET NOTE
# ==========================================================

@app.route(
    "/delete",
    methods=["POST"]
)
def delete_note():


    note_id =
        request.form.get(
            "id"
        )


    if note_id:


        with get_connection() as connection:


            with connection.cursor() as cursor:


                cursor.execute(
                    """
                    DELETE FROM notes

                    WHERE id = %s
                    """,
                    (note_id,)
                )


            connection.commit()


    return redirect("/")


# ==========================================================
# START
# ==========================================================

create_table()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )