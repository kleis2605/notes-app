from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

NOTES_FILE = "notes.txt"


# --------------------------------------------------
# HENT NOTER FRA FIL
# --------------------------------------------------

def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:

            notes = []

            for line in file:

                note = line.strip()

                if note:
                    notes.append(note)

            return notes

    except FileNotFoundError:
        return []


# --------------------------------------------------
# GEM NOTER I FIL
# --------------------------------------------------

def save_notes(notes):

    with open(NOTES_FILE, "w", encoding="utf-8") as file:

        for note in notes:
            file.write(note + "\n")


# --------------------------------------------------
# HENT NOTER VED START
# --------------------------------------------------

notes = load_notes()


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


        /* --------------------------------------------------
           TOPBAR
        -------------------------------------------------- */

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


        /* --------------------------------------------------
           NOTER
        -------------------------------------------------- */

        .notes {
            padding: 20px;
        }


        .note-card {
            background: #1b1b1b;

            border: 1px solid #292929;

            border-radius: 18px;

            padding: 18px;

            margin-bottom: 14px;

            box-shadow:
                0 8px 25px
                rgba(0, 0, 0, 0.2);
        }


        .note-text {
            font-size: 17px;

            line-height: 1.5;

            overflow-wrap: anywhere;

            white-space: pre-wrap;
        }


        /* --------------------------------------------------
           KNAPPER UNDER NOTEN
        -------------------------------------------------- */

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

            transition:
                background 0.15s,
                transform 0.15s;
        }


        .action-button:active {
            transform: scale(0.94);
        }


        /* REDIGER KNAP */

        .edit-button {
            background: #292929;

            color: #e5e5e5;
        }


        .edit-button:hover {
            background: #383838;
        }


        /* SLET KNAP */

        .delete-button {
            background: transparent;

            color: #ff5c5c;

            border: 1px solid #4b2626;
        }


        .delete-button:hover {
            background: #351919;
        }


        /* --------------------------------------------------
           PLUS KNAP
        -------------------------------------------------- */

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

            transition:
                transform 0.15s;
        }


        .add-button:hover {
            transform: scale(1.05);
        }


        .add-button:active {
            transform: scale(0.92);
        }


        /* --------------------------------------------------
           GENEREL POPUP BAGGRUND
        -------------------------------------------------- */

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


        /* --------------------------------------------------
           GENEREL POPUP
        -------------------------------------------------- */

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

            animation:
                popup 0.18s ease-out;
        }


        @keyframes popup {

            from {
                opacity: 0;
                transform: scale(0.94);
            }

            to {
                opacity: 1;
                transform: scale(1);
            }

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


        textarea:focus {
            border-color: #777;
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


        /* --------------------------------------------------
           SLET POPUP
        -------------------------------------------------- */

        .delete-modal {
            max-width: 380px;
        }


        .delete-icon {
            width: 54px;

            height: 54px;

            display: flex;

            justify-content: center;

            align-items: center;

            margin-bottom: 16px;

            border-radius: 16px;

            background: #351919;

            color: #ff5c5c;

            font-size: 25px;

            font-weight: bold;
        }


        .delete-modal h2 {
            margin-bottom: 8px;
        }


        .delete-modal p {
            margin: 0;

            color: #999;

            line-height: 1.5;
        }


        .delete-preview {
            margin-top: 16px;

            padding: 14px;

            background: #111;

            border: 1px solid #292929;

            border-radius: 14px;

            color: #ddd;

            overflow-wrap: anywhere;

            max-height: 120px;

            overflow-y: auto;
        }


        .delete-confirm {
            background: #d84040;

            color: white;

            font-weight: 600;
        }


        .delete-confirm:hover {
            background: #ec4b4b;
        }


        /* --------------------------------------------------
           INGEN NOTER
        -------------------------------------------------- */

        .empty-state {
            text-align: center;

            margin-top: 100px;

            color: #777;
        }


        .empty-icon {
            font-size: 55px;
        }


        .empty-state h2 {
            color: #aaa;

            margin-bottom: 5px;
        }


        .empty-state p {
            margin-top: 0;
        }


        /* --------------------------------------------------
           PC
        -------------------------------------------------- */

        @media (min-width: 650px) {

            .add-button {
                right: calc(50% - 300px);
            }

        }

    </style>

</head>


<body>


    <div class="app">


        <!-- TOPBAR -->

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



        <!-- NOTER -->

        <div class="notes">


            {% if notes %}


                {% for note in notes %}


                    <div
                        class="note-card"
                        data-index="{{ loop.index0 }}"
                    >


                        <div class="note-text">

                            {{ note }}

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



    <!-- PLUS KNAP -->

    <button
        class="add-button"
        onclick="openAddModal()"
    >
        +
    </button>



    <!-- --------------------------------------------------
         NY NOTE POPUP
    -------------------------------------------------- -->

    <div
        class="modal-background"
        id="addModal"
        onclick="closeAddModalFromBackground(event)"
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
                        onclick="closeAddModal()"
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



    <!-- --------------------------------------------------
         REDIGER POPUP
    -------------------------------------------------- -->

    <div
        class="modal-background"
        id="editModal"
        onclick="closeEditModalFromBackground(event)"
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
                    name="index"
                    id="editIndex"
                >


                <textarea
                    name="note"
                    id="editNoteInput"
                    required
                ></textarea>


                <div class="modal-buttons">


                    <button
                        type="button"
                        class="cancel-button"
                        onclick="closeEditModal()"
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



    <!-- --------------------------------------------------
         SLET POPUP
    -------------------------------------------------- -->

    <div
        class="modal-background"
        id="deleteModal"
        onclick="closeDeleteModalFromBackground(event)"
    >


        <div class="modal delete-modal">


            <div class="delete-icon">
                !
            </div>


            <h2>
                Slet note?
            </h2>


            <p>
                Er du sikker? Denne handling kan ikke fortrydes.
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
                    name="index"
                    id="deleteIndex"
                >


                <div class="modal-buttons">


                    <button
                        type="button"
                        class="cancel-button"
                        onclick="closeDeleteModal()"
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



    <!-- --------------------------------------------------
         JAVASCRIPT
    -------------------------------------------------- -->

    <script>


        // --------------------------------------------------
        // NY NOTE
        // --------------------------------------------------

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


        function closeAddModal() {

            document
                .getElementById("addModal")
                .classList
                .remove("show");

        }


        function closeAddModalFromBackground(event) {

            if (event.target.id === "addModal") {

                closeAddModal();

            }

        }



        // --------------------------------------------------
        // REDIGER NOTE
        // --------------------------------------------------

        function openEditModal(button) {

            // Find hele note-kortet
            const card =
                button.closest(".note-card");


            // Hent note-nummeret
            const index =
                card.dataset.index;


            // Hent note-teksten
            const noteText =
                card
                    .querySelector(".note-text")
                    .textContent
                    .trim();


            // Find popup
            const modal =
                document.getElementById("editModal");


            // Find skjult index-felt
            const indexInput =
                document.getElementById("editIndex");


            // Find textarea
            const editInput =
                document.getElementById("editNoteInput");


            // Gem note-nummer
            indexInput.value = index;


            // Put eksisterende tekst ind
            editInput.value = noteText;


            // Vis popup
            modal.classList.add("show");


            setTimeout(function() {

                editInput.focus();

                editInput.setSelectionRange(
                    editInput.value.length,
                    editInput.value.length
                );

            }, 100);

        }


        function closeEditModal() {

            document
                .getElementById("editModal")
                .classList
                .remove("show");

        }


        function closeEditModalFromBackground(event) {

            if (event.target.id === "editModal") {

                closeEditModal();

            }

        }



        // --------------------------------------------------
        // SLET NOTE
        // --------------------------------------------------

        function openDeleteModal(button) {

            // Find note-kortet
            const card =
                button.closest(".note-card");


            // Hent note-nummer
            const index =
                card.dataset.index;


            // Hent note-tekst
            const noteText =
                card
                    .querySelector(".note-text")
                    .textContent
                    .trim();


            // Find popup
            const modal =
                document.getElementById("deleteModal");


            // Find preview
            const preview =
                document.getElementById("deletePreview");


            // Find skjult index-felt
            const indexInput =
                document.getElementById("deleteIndex");


            // Vis teksten
            preview.textContent = noteText;


            // Gem index
            indexInput.value = index;


            // Vis popup
            modal.classList.add("show");

        }


        function closeDeleteModal() {

            document
                .getElementById("deleteModal")
                .classList
                .remove("show");

        }


        function closeDeleteModalFromBackground(event) {

            if (event.target.id === "deleteModal") {

                closeDeleteModal();

            }

        }



        // --------------------------------------------------
        // ESCAPE LUKKER ALLE POPUPS
        // --------------------------------------------------

        document.addEventListener(
            "keydown",
            function(event) {

                if (event.key === "Escape") {

                    closeAddModal();

                    closeEditModal();

                    closeDeleteModal();

                }

            }
        );


    </script>


</body>

</html>
"""


# --------------------------------------------------
# FORSIDE + NY NOTE
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    global notes


    if request.method == "POST":

        new_note = request.form.get(
            "note",
            ""
        ).strip()


        if new_note:

            notes.append(new_note)

            save_notes(notes)


        return redirect("/")


    return render_template_string(
        PAGE,
        notes=notes
    )


# --------------------------------------------------
# REDIGER NOTE
# --------------------------------------------------

@app.route("/edit", methods=["POST"])
def edit_note():

    global notes


    index = request.form.get("index")

    new_note = request.form.get(
        "note",
        ""
    ).strip()


    if index is not None:

        try:

            index = int(index)

        except ValueError:

            return redirect("/")


        if (
            0 <= index < len(notes)
            and new_note
        ):

            # Erstat den gamle note
            notes[index] = new_note


            # Gem ændringen i notes.txt
            save_notes(notes)


    return redirect("/")


# --------------------------------------------------
# SLET NOTE
# --------------------------------------------------

@app.route("/delete", methods=["POST"])
def delete_note():

    global notes


    index = request.form.get("index")


    if index is not None:

        try:

            index = int(index)

        except ValueError:

            return redirect("/")


        if 0 <= index < len(notes):

            notes.pop(index)

            save_notes(notes)


    return redirect("/")


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )