/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

class ItParcDashboard extends Component {
    static template = "it_parc.dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            totalEquipments: 0,
            assignedCount: 0,
            maintenanceCount: 0,
            retiredCount: 0,
            draftCount: 0,
            alertCount: 0,
            activeContractCount: 0,
            totalMaintenanceCost: 0,
            expiringWarrantyCount: 0,
            chartData: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            const equipmentData = await this.orm.searchRead(
                "it.equipment",
                [],
                ["id", "state", "purchase_value"],
                {}
            );

            const alertCount = await this.orm.searchCount("it.alert", [
                ["state", "=", "pending"],
            ]);

            const activeContractCount = await this.orm.searchCount("it.contract", [
                ["state", "=", "active"],
            ]);

            const expiringWarranty = await this.orm.searchCount("it.equipment", [
                ["warranty_remaining_days", ">", 0],
                ["warranty_remaining_days", "<=", 30],
                ["state", "!=", "retired"],
            ]);

            const totalCosts = await this.orm.readGroup(
                "it.intervention",
                [],
                ["cost:sum"],
                ["equipment_id"],
            );

            const totalMaintenanceCost = totalCosts.reduce(
                (sum, g) => sum + (g.__count || 0),
                0
            );

            const totalCost = totalCosts.reduce(
                (sum, g) => sum + (g.cost || 0),
                0
            );

            const totalEquipments = equipmentData.length;
            const assignedCount = equipmentData.filter(
                (e) => e.state === "assigned"
            ).length;
            const maintenanceCount = equipmentData.filter(
                (e) => e.state === "maintenance"
            ).length;
            const retiredCount = equipmentData.filter(
                (e) => e.state === "retired"
            ).length;
            const draftCount = equipmentData.filter(
                (e) => e.state === "draft"
            ).length;

            const stateGroups = {
                draft: draftCount,
                assigned: assignedCount,
                maintenance: maintenanceCount,
                retired: retiredCount,
            };

            const chartData = Object.entries(stateGroups)
                .filter(([_, v]) => v > 0)
                .map(([state, count]) => {
                    const labels = {
                        draft: "Brouillon",
                        assigned: "Affecté",
                        maintenance: "En maintenance",
                        retired: "Retiré",
                    };
                    return { label: labels[state] || state, value: count };
                });

            Object.assign(this.state, {
                loading: false,
                totalEquipments,
                assignedCount,
                maintenanceCount,
                retiredCount,
                draftCount,
                alertCount,
                activeContractCount,
                totalMaintenanceCost: totalCost,
                expiringWarrantyCount: expiringWarranty,
                chartData,
            });
        } catch (error) {
            console.error("Dashboard load error:", error);
            this.state.loading = false;
        }
    }

    openEquipments() {
        this.action.doAction("it_parc.action_it_equipment");
    }

    openAlerts() {
        this.action.doAction("it_parc.action_it_alert");
    }

    openContracts() {
        this.action.doAction("it_parc.action_it_contract");
    }

    openInterventions() {
        this.action.doAction("it_parc.action_it_intervention");
    }
}

registry
    .category("actions")
    .add("it_parc_dashboard", ItParcDashboard);
