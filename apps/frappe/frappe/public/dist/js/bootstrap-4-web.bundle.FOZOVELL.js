(()=>{$(".dropdown-menu a.dropdown-toggle").on("click",function(e){e.preventDefault(),e.stopImmediatePropagation(),$(this).next().hasClass("show")||$(this).parents(".dropdown-menu").first().find(".show").removeClass("show");var o=$(this).next(".dropdown-menu");return o.toggleClass("show"),$(this).parents("li.nav-item.dropdown.show").on("hidden.bs.dropdown",function(){$(".dropdown-submenu .show").removeClass("show")}),!1});frappe.get_modal=function(e,o){return $(`<div class="modal" tabindex="-1" role="dialog">
			<div class="modal-dialog modal-dialog-scrollable" role="document">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title">${e}</h5>
						<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						${frappe.utils.icon("close-alt","sm","close-alt")}
						</button>
					</div>
					<div class="modal-body">
						${o}
					</div>
					<div class="modal-footer hidden">
						<button type="button" class="btn btn-sm btn-secondary hidden"></button>
						<button type="button" class="btn btn-sm btn-primary hidden"></button>
					</div>
				</div>
			</div>
		</div>`)};frappe.ui.Dialog=class extends frappe.ui.Dialog{get_primary_btn(){return this.$wrapper.find(".modal-footer .btn-primary")}get_secondary_btn(){return this.$wrapper.find(".modal-footer .btn-secondary")}set_primary_action(o,s){return this.$wrapper.find(".modal-footer").removeClass("hidden"),super.set_primary_action(o,s).removeClass("hidden")}set_secondary_action(o){return super.set_secondary_action(o).removeClass("hidden")}make(){super.make(),this.fields&&this.$wrapper.find(".section-body").addClass("w-100")}};})();
//# sourceMappingURL=bootstrap-4-web.bundle.FOZOVELL.js.map
