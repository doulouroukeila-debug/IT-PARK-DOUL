/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            data: null,
            loading: true,
            error: false,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.loading = true;
            const data = await this.orm.call("it.equipment", "get_dashboard_data", []);
            this.state.data = data;
            this.state.loading = false;
        } catch (err) {
            this.state.error = true;
            this.state.loading = false;
            console.error("Dashboard data load error:", err);
        }
    }
}

registry.category("actions").add("it_parc_dashboard", ItParcDashboard);

export default ItParcDashboard;
