frappe.pages['reset-data'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
	  parent: wrapper,
	  title: 'Reset data',
	  single_column: true
	});

	// Liste des tables à réinitialiser
	const tables = [
	  { id: 'table1', name: 'Utilisateurs' },
	  { id: 'table2', name: 'Commandes' },
	  { id: 'table3', name: 'Produits' },
	  { id: 'table4', name: 'Factures' },
	  { id: 'table5', name: 'Clients' },
	  { id: 'table6', name: 'Fournisseurs' },
	  { id: 'table7', name: 'Transactions' },
	  { id: 'table8', name: 'Inventaire' }
	];
  
	// Créer le formulaire de réinitialisation
	let tableCheckboxes = '';
	tables.forEach(table => {
	  tableCheckboxes += `
		<div class="table-option">
		  <input type="checkbox" id="${table.id}" name="tables" value="${table.id}">
		  <label for="${table.id}">${table.name}</label>
		</div>
	  `;
	});
  
	const resetForm = `
	  <div class="reset-container">
		<div class="reset-card">
		  <h3 class="reset-title">Réinitialiser les données des tables suivantes :</h3>
		  
		  <div class="tables-container">
			${tableCheckboxes}
			<div class="select-all-container">
			  <input type="checkbox" id="select-all" name="select-all">
			  <label for="select-all"><strong>Sélectionner toutes les tables</strong></label>
			</div>
		  </div>
		  
		  <div class="verification-container">
			<div class="verification-box">
			  <label for="verification">
				<input type="checkbox" id="verification" name="verification">
				Je confirme vouloir réinitialiser les tables sélectionnées. Cette action est irréversible.
			  </label>
			</div>
		  </div>
		  
		  <div class="action-buttons">
			<button class="btn btn-sm btn-default back-btn">Annuler</button>
			<button class="btn btn-sm btn-primary reset-btn" disabled>Réinitialiser</button>
		  </div>
		</div>
	  </div>
	`;
  
	$(page.body).html(resetForm);
  
	// Ajouter le CSS à la page
	$(`<style>
	  .reset-container {
		display: flex;
		justify-content: center;
		padding: 20px;
		background-color: #f9f9f9;
		min-height: calc(100vh - 160px);
	  }
	  .reset-card {
		background-color: #ffffff;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		padding: 30px;
		max-width: 1000px;
		width: 100%;
		color: #333333;
		border: 1px solid #dddddd;
	  }
	  .reset-title {
		color: #222222;
		margin-top: 0;
		margin-bottom: 20px;
		font-size: 24px;
		border-bottom: 1px solid #eeeeee;
		padding-bottom: 10px;
	  }
	  .tables-container {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		grid-gap: 10px;
		margin-bottom: 25px;
	  }
	  .table-option {
		padding: 10px 15px;
		background-color: #f5f5f5;
		border-radius: 4px;
		border-left: 3px solid #bdbdbd;
		transition: background-color 0.2s;
		display: flex;
		align-items: center;
	  }
	  .table-option:hover {
		background-color: #eeeeee;
	  }
	  .table-option input[type="checkbox"] {
		margin-right: 10px;
	  }
	  .table-option label{
		margin-top: 8px;
	  }
	  .select-all-container {
		grid-column: span 2;
		padding: 10px 15px;
		margin-top: 10px;
		background-color: #e8f5e9;
		border-radius: 4px;
		border-left: 3px solid #2e7d32;
		display: flex;
		align-items: center;
	  }
	  .select-all-container input[type="checkbox"] {
		margin-right: 10px;
	  }
	  .verification-container {
		margin-bottom: 25px;
		padding: 15px;
		background-color: #ffebee;
		border-left: 4px solid #c62828;
		border-radius: 4px;
	  }
	  .verification-box {
		display: flex;
		align-items: center;
	  }
	  .verification-box input[type="checkbox"] {
		margin-right: 10px;
	  }
	  .verification-box label {
		color: #c62828;
		font-weight: bold;
	  }
	  .action-buttons {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		margin-top: 20px;
	  }
	  .reset-btn {
		background-color: #c62828;
		color: white;
		border-color: #c62828;
	  }
	  .reset-btn:hover {
		background-color: #b71c1c;
		border-color: #b71c1c;
	  }
	  .reset-btn:disabled {
		background-color: #e57373;
		border-color: #e57373;
		cursor: not-allowed;
	  }
	</style>`).appendTo(page.body);
  
	// Gérer l'activation du bouton de réinitialisation
	function updateResetButton() {
	  if ($('#verification').is(':checked') && $('input[name="tables"]:checked').length > 0) {
		$('.reset-btn').prop('disabled', false);
	  } else {
		$('.reset-btn').prop('disabled', true);
	  }
	}
  
	$('#verification').on('change', updateResetButton);
	$('input[name="tables"]').on('change', updateResetButton);
  
	// Gérer l'option "Sélectionner toutes les tables"
	$('#select-all').on('change', function() {
	  if ($(this).is(':checked')) {
		$('input[name="tables"]').prop('checked', true);
	  } else {
		$('input[name="tables"]').prop('checked', false);
	  }
	  updateResetButton();
	});
  
	// Mettre à jour la case "Sélectionner toutes les tables" si toutes les tables sont sélectionnées
	$('input[name="tables"]').on('change', function() {
	  if ($('input[name="tables"]:checked').length === $('input[name="tables"]').length) {
		$('#select-all').prop('checked', true);
	  } else {
		$('#select-all').prop('checked', false);
	  }
	});
  
	// Gérer le bouton d'annulation
	$('.back-btn').on('click', function() {
	  window.history.back();
	});
  
	// Gérer le bouton de réinitialisation
	$('.reset-btn').on('click', function() {
	  const selectedTables = [];
	  $('input[name="tables"]:checked').each(function() {
		const tableId = $(this).val();
		const tableName = $(this).next('label').text();
		selectedTables.push({ id: tableId, name: tableName });
	  });
  
	  frappe.confirm(
		`Êtes-vous sûr de vouloir réinitialiser les ${selectedTables.length} tables sélectionnées ?`,
		function() {
		  // Action après confirmation
		  frappe.show_alert({
			message: 'Réinitialisation en cours...',
			indicator: 'orange'
		  });
  
		  // Simuler une requête AJAX (à remplacer par votre appel réel)
		  setTimeout(function() {
			const results = {};
			selectedTables.forEach(table => {
			  results[table.name] = 'Réinitialisé avec succès';
			});
  
			const response = {
			  status: 'success',
			  message: `Réinitialisation de ${selectedTables.length} tables effectuée avec succès`,
			  results: results
			};
  
			// Rediriger vers la page de réussite avec les données
			const encodedData = encodeURIComponent(JSON.stringify(response));
			window.location.href = '/app/reset-data?data=' + encodedData;
		  }, 2000);
		}
	  );
	});
  };