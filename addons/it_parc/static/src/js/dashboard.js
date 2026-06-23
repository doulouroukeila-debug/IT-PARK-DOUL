/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";
}

registry.category("actions").add("it_parc_dashboard", ItParcDashboard);
export default ItParcDashboard;
