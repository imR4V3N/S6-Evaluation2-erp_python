frappe.pages['import_data'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Import Data',
        single_column: true
    });

    // Ajouter le HTML du formulaire
    $(wrapper).find('.layout-main-section').html(`
        <div class="import-container">
            <p class="status-msg"></p>
            <p>Select CSV files to import:</p>
            <form id="import-form" enctype="multipart/form-data" method="POST">
                <div class="form-group">
                    <label for="file1">File 1 (Material Request & Item):</label>
                    <input type="file" id="file1" name="file1" class="form-control" accept=".csv" required>
                </div>
                <div class="form-group">
                    <label for="file2">File 2 (Supplier):</label>
                    <input type="file" id="file2" name="file2" class="form-control" accept=".csv" required>
                </div>
                <div class="form-group">
                    <label for="file3">File 3 (Request for Quotation):</label>
                    <input type="file" id="file3" name="file3" class="form-control" accept=".csv" required>
                </div>
                <button type="submit" id="btn-submit" class="btn btn-primary">Importer les données</button>
            </form>
        </div>
    `);

    // Style CSS
    $(`<style>
        .import-container {
            margin-top: 30px;
            background-color: #ffffff;
            padding: 25px 40px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .import-container p {
            font-size: 15px;
            color: #555;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-control {
            font-size: 14px;
            padding: 10px;
            height: 40px;
            border-radius: 5px;
            width: 100%;
        }
        .import-container .btn {
            margin-top: 15px;
            padding: 10px 20px;
            font-size: 15px;
            border: none;
            border-radius: 5px;
            background-color: #383838;
            color: white;
            cursor: pointer;
        }
        .import-container .btn:hover {
            background-color: #222222;
        }
        .status-msg {
            margin-top: 15px;
            font-weight: bold;
            color: #5bc85c;
        }
    </style>`).appendTo('head');
    
    
    // Fonction d'import
    async function postFiles(e) {
        const csrfToken = frappe.csrf_token;
        e.preventDefault();

        const root_element = wrapper;
        const formData = new FormData();

        const suppliersFile = root_element.querySelector("#file2").files[0];
        const quotationsFile = root_element.querySelector("#file1").files[0];
        const quotationSuppliersFile = root_element.querySelector("#file3").files[0];

        if (suppliersFile) formData.append("file2", suppliersFile);
        if (quotationsFile) formData.append("file1", quotationsFile);
        if (quotationSuppliersFile) formData.append("file3", quotationSuppliersFile);

        const $msg = $(root_element).find(".status-msg");
        const $btn = $(root_element).find("#btn-submit");

        $msg.css('color', '#999').text("Importation des données...");
        $btn.prop('disabled', true).text("Importation...");

        try {
            const response = await fetch("/api/method/erpnext.data.data_controller.import_data", {
                method: "POST",
                body: formData,
                headers: {
                    "X-Frappe-CSRF-Token": csrfToken
                }
            });

            const result = await response.json();

            if (response.ok && result.message) {
                $msg.css('color', '#5cb85c').text(result.message);
            } else {
                $msg.css('color', '#d9534f').html(
                    result._server_messages
                        ? JSON.parse(result._server_messages).join("<br>")
                        : result.message || "Erreur inconnue."
                );
            }
        } catch (error) {
            $msg.css('color', '#d9534f').text("Erreur réseau ou serveur : " + error.message);
        }

        $btn.prop('disabled', false).text("Importer les données");
    }

    // Bind submit
    wrapper.querySelector('#btn-submit').onclick = postFiles;
}
