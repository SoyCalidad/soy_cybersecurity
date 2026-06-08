/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { LoginPopup} from "@menus_hola_calidad/app/components/login_popup/login_popup";


patch(LoginPopup.prototype, {
    async openIS() {
        const menu = this.menuService.getAll().find(menu => menu.xmlid=="soy_cybersecurity_cybersecurity.menu_cybersecurity_root");
        if (menu) {
            await this.menuService.selectMenu(menu);
        }
    }

})
