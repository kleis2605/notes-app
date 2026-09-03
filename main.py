from flask import Flask, request, redirect, render_template_string
import os
import psycopg

app = Flask(__name__)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_table():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)

        connection.commit()


def load_notes():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, text
                FROM notes
                ORDER BY id DESC
            """)

            return cursor.fetchall()


# --------------------------------------------------
# HTML
# --------------------------------------------------

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
        content="#0f0f0f"
    >

    <title>Mine Noter</title>


    <style>

        * {
            box-sizing: border-box;
        }


        body {
            margin: 0;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;

            background: #0f0f0f;

            color: white;

            min-height: 100vh;
        }


        .app {
            width: 100%;

            max-width: 650px;

            margin: 0 auto;

            min-height: 100vh;

            padding-bottom: 120px;
        }


        .topbar {
            position: sticky;

            top: 0;

            z-index: 10;

            padding: 22px 20px 18px;

            background: rgba(15, 15, 15, 0.92);

            backdrop-filter: blur(15px);

            border-bottom: 1px solid #252525;
        }


        .topbar h1 {
            margin: 0;

            font-size: 30px;
        }


        .topbar p {
            margin: 5px 0 0;

            color: #888;

            font-size: 14px;
        }


        .notes {
            padding: 20px;
        }


        .note-card {
            background: #1b1b1b;

            border: 1px solid #292929;

            border-radius: 18px;

            padding: 18px;

            margin-bottom: 14px;
        }


        .note-text {
            font-size: 17px;

            line-height: 1.5;

            overflow-wrap: anywhere;

            white-space: pre-wrap;
        }


        .note-actions {
            display: flex;

            justify-content: flex-end;

            gap: 8px;

            margin-top: 16px;
        }


        .action-button {
            border: none;

            border-radius: 10px;

            padding: 9px 14px;

            font-size: 14px;

            font-weight: 500;

            cursor: pointer;
        }


        .edit-button {
            background: #292929;

            color: #e5e5e5;
        }


        .delete-button {
            background: transparent;

            color: #ff5c5c;

            border: 1px solid #4b2626;
        }


        .add-button {
            position: fixed;

            right: 24px;

            bottom: 28px;

            width: 64px;

            height: 64px;

            border: none;

            border-radius: 50%;

            background: white;

            color: black;

            font-size: 36px;

            cursor: pointer;

            box-shadow:
                0 12px 35px
                rgba(0, 0, 0, 0.5);

            z-index: 20;
        }


        .modal-background {
            position: fixed;

            inset: 0;

            display: none;

            justify-content: center;

            align-items: center;

            padding: 20px;

            background:
                rgba(0, 0, 0, 0.72);

            backdrop-filter: blur(8px);

            z-index: 100;
        }


        .modal-background.show {
            display: flex;
        }


        .modal {
            width: 100%;

            max-width: 500px;

            background: #1b1b1b;

            border: 1px solid #2d2d2d;

            border-radius: 22px;

            padding: 24px;

            box-shadow:
                0 20px 60px
                rgba(0, 0, 0, 0.5);
        }


        .modal h2 {
            margin: 0 0 18px;
        }


        textarea {
            width: 100%;

            min-height: 150px;

            resize: vertical;

            padding: 15px;

            border: 1px solid #333;

            border-radius: 15px;

            background: #111;

            color: white;

            font-family: inherit;

            font-size: 17px;

            outline: none;
        }


        .modal-buttons {
            display: flex;

            gap: 10px;

            margin-top: 15px;
        }


        .modal-buttons button {
            flex: 1;

            padding: 14px;

            border: none;

            border-radius: 14px;

            font-size: 16px;

            cursor: pointer;
        }


        .cancel-button {
            background: #292929;

            color: white;
        }


        .save-button {
            background: white;

            color: black;

            font-weight: 600;
        }


        .delete-confirm {
            background: #d84040;

            color: white;

            font-weight: 600;
        }


        .delete-preview {
            margin-top: 16px;

            padding: 14px;

            background: #111;

            border: 1px solid #292929;

            border-radius: 14px;

            color: #ddd;
        }


        .empty-state {
            text-align: center;

            margin-top: 100px;

            color: #777;
        }


        .empty-icon {
            font-size: 55px;
        }


        @media (min-width: 650px) {

            .add-button {
                right: calc(50% - 300px);
            }

        }

    </style>

</head>


<body>


    <div class="app">


        <div class="topbar">

            <h1>
                Mine noter
            </h1>

            <p>

                {{ notes|length }}

                {% if notes|length == 1 %}

                    note gemt

                {% else %}

                    noter gemt

                {% endif %}

            </p>

        </div>


        <div class="notes">


            {% if notes %}


                {% for note in notes %}


                    <div
                        class="note-card"
                        data-id="{{ note[0] }}"
                    >


                        <div class="note-text">

                            {{ note[1] }}

                        </div>


                        <div class="note-actions">


                            <button
                                class="action-button edit-button"
                                type="button"
                                onclick="openEditModal(this)"
                            >
                                Rediger
                            </button>


                            <button
                                class="action-button delete-button"
                                type="button"
                                onclick="openDeleteModal(this)"
                            >
                                Slet
                            </button>


                        </div>


                    </div>


                {% endfor %}


            {% else %}


                <div class="empty-state">

                    <div class="empty-icon">
                        📝
                    </div>

                    <h2>
                        Ingen noter endnu
                    </h2>

                    <p>
                        Tryk på + for at lave din første note
                    </p>

                </div>


            {% endif %}


        </div>

    </div>


    <button
        class="add-button"
        onclick="openAddModal()"
    >
        +
    </button>


    <!-- NY NOTE -->

    <div
        class="modal-background"
        id="addModal"
        onclick="closeBackground(event, 'addModal')"
    >

        <div class="modal">

            <h2>
                Ny note
            </h2>


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
                        onclick="closeModal('addModal')"
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


    <!-- REDIGER -->

    <div
        class="modal-background"
        id="editModal"
        onclick="closeBackground(event, 'editModal')"
    >

        <div class="modal">


            <h2>
                Rediger note
            </h2>


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
                        onclick="closeModal('editModal')"
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


    <!-- SLET -->

    <div
        class="modal-background"
        id="deleteModal"
        onclick="closeBackground(event, 'deleteModal')"
    >

        <div class="modal">


            <h2>
                Slet note?
            </h2>


            <p>
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
                        onclick="closeModal('deleteModal')"
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


    <script>


        function openAddModal() {

            const modal =
                document.getElementById("addModal");

            const input =
                document.getElementById("noteInput");

            modal.classList.add("show");

            setTimeout(function() {
                input.focus();
            }, 100);

        }


        function openEditModal(button) {

            const card =
                button.closest(".note-card");

            const id =
                card.dataset.id;

            const text =
                card
                    .querySelector(".note-text")
                    .textContent
                    .trim();

            document.getElementById("editId").value =
                id;

            document.getElementById("editNote").value =
                text;

            document
                .getElementById("editModal")
                .classList
                .add("show");

        }


        function openDeleteModal(button) {

            const card =
                button.closest(".note-card");

            const id =
                card.dataset.id;

            const text =
                card
                    .querySelector(".note-text")
                    .textContent
                    .trim();

            document.getElementById("deleteId").value =
                id;

            document.getElementById("deletePreview").textContent =
                text;

            document
                .getElementById("deleteModal")
                .classList
                .add("show");

        }


        function closeModal(id) {

            document
                .getElementById(id)
                .classList
                .remove("show");

        }


        function closeBackground(event, id) {

            if (event.target.id === id) {

                closeModal(id);

            }

        }


        document.addEventListener(
            "keydown",
            function(event) {

                if (event.key === "Escape") {

                    closeModal("addModal");

                    closeModal("editModal");

                    closeModal("deleteModal");

                }

            }
        );


    </script>


</body>

</html>
"""


# --------------------------------------------------
# FORSIDE + OPRET NOTE
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

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
                        INSERT INTO notes (text)
                        VALUES (%s)
                        """,
                        (note,)
                    )

                connection.commit()


        return redirect("/")


    notes = load_notes()


    return render_template_string(
        PAGE,
        notes=notes
    )


# --------------------------------------------------
# REDIGER NOTE
# --------------------------------------------------

@app.route("/edit", methods=["POST"])
def edit_note():

    note_id = request.form.get("id")

    note = request.form.get(
        "note",
        ""
    ).strip()


    if note_id and note:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE notes
                    SET text = %s
                    WHERE id = %s
                    """,
                    (
                        note,
                        note_id
                    )
                )

            connection.commit()


    return redirect("/")


# --------------------------------------------------
# SLET NOTE
# --------------------------------------------------

@app.route("/delete", methods=["POST"])
def delete_note():

    note_id = request.form.get("id")


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


# --------------------------------------------------
# START
# --------------------------------------------------

create_table()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )