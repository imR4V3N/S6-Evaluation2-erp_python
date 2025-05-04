frappe.pages['reset-data'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Reset Data',
		single_column: true
	});

	$(wrapper).find('.layout-main-section').html(`
		<div class="reset-container">
			<p class="status-msg"></p>
			<p>Select the Doctypes to reset:</p>
			<form id="reset-form">
				<div class="checkbox-grid">
					<label><input type="checkbox" id="select-all" /> <strong>All</strong></label><br>
					<label><input type="checkbox" name="doctypes" value="Item" /> Item</label>
					<label><input type="checkbox" name="doctypes" value="Supplier" /> Supplier</label>
					<label><input type="checkbox" name="doctypes" value="Material Request" /> Material Request</label>
					<label><input type="checkbox" name="doctypes" value="Request for Quotation" /> Request for Quotation</label>
					<label><input type="checkbox" name="doctypes" value="Supplier Quotation" /> Supplier Quotation</label>
					<label><input type="checkbox" name="doctypes" value="Purchase Order" /> Purchase Order</label>
					<label><input type="checkbox" name="doctypes" value="Purchase Invoice" /> Purchase Invoice</label>
					<label><input type="checkbox" name="doctypes" value="Purchase Receipt" /> Purchase Receipt</label>
					<label><input type="checkbox" name="doctypes" value="Stock Entry" /> Stock Entry</label>
					<label><input type="checkbox" name="doctypes" value="GL Entry" /> GL Entry</label>
					<label><input type="checkbox" name="doctypes" value="Payment Entry" /> Payment Entry</label>
					<label><input type="checkbox" name="doctypes" value="Communication" /> Communication</label>
					<label><input type="checkbox" name="doctypes" value="Activity Log" /> Activity Log</label>
					<label><input type="checkbox" name="doctypes" value="File" /> File</label>
					<label><input type="checkbox" name="doctypes" value="ToDo" /> ToDo</label>
					<label><input type="checkbox" name="doctypes" value="Workflow Action" /> Workflow Action</label>
				</div>
				<button type="submit" class="btn btn-danger">Reset Selected</button>
			</form>
		</div>
	`);

	$(`<style>
		.reset-container {
			margin-top: 30px;
			background-color: #ffffff;
			padding: 25px 40px;
			border-radius: 10px;
			box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
			max-width: 800px;
			margin-left: auto;
			margin-right: auto;
		}
		.reset-container h2 {
			color: #d9534f;
			margin-bottom: 20px;
		}
		.reset-container p {
			font-size: 15px;
			color: #555;
		}
		.checkbox-grid {
			display: grid;
			grid-template-columns: repeat(3, 1fr);
			gap: 10px;
			margin: 20px 0;
		}
		.checkbox-grid label {
			display: flex;
			align-items: center;
			font-size: 14px;
		}
		.reset-container .btn {
			margin-top: 15px;
			padding: 10px 20px;
			font-size: 15px;
			border: none;
			border-radius: 5px;
			background-color:#383838;
			color: white;
			cursor: pointer;
		}
		.reset-container .btn:hover {
			background-color: #222222;
		}
		.status-msg {
			margin-top: 15px;
			font-weight: bold;
			color: #5cb85c;
		}
	</style>`).appendTo('head');
	


	$('#reset-form').on('submit', function(e) {
		e.preventDefault();
		const selected = [];
		$('#reset-form input[name="doctypes"]:checked').each(function() {
			selected.push($(this).val());
		});
	
		if (selected.length === 0) {
			frappe.msgprint(__('Please select at least one Doctype.'));
			return;
		}
	
		$('.status-msg').css('color', '#999').text("Resetting data...");
		const $btn = $('.btn-danger');
		$btn.prop('disabled', true).text("Resetting...");
	
		frappe.call({
			method: "erpnext.data.data_controller.reset_data",
			args: { doctypes: selected },
			callback: function(r) {
				if (!r.exc) {
					$('.status-msg').css('color', '#5cb85c').text("Data reset successfully.");
				} else {
					$('.status-msg').css('color', '#d9534f').text("Error during reset data.");
				}
				$btn.prop('disabled', false).text("Reset Selected");
			}
		});
	});
	

	$(wrapper).on('change', '#select-all', function() {
		const isChecked = $(this).is(':checked');
		$('#reset-form input[name="doctypes"]').prop('checked', isChecked);
	});

	$(wrapper).on('change', 'input[name="doctypes"]', function() {
		if (!$(this).is(':checked')) {
			$('#select-all').prop('checked', false);
		} else {
			const allChecked = $('input[name="doctypes"]').length === $('input[name="doctypes"]:checked').length;
			$('#select-all').prop('checked', allChecked);
		}
	});
  };