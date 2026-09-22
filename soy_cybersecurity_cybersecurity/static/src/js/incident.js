/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CybersecurityIncident = publicWidget.Widget.extend({
    selector: "#incidentForm",

    events: {
        "click .next": "_onNext",
        "click .previous": "_onPrevious",
        "change #complainer_delivery_type": "_onDeliveryTypeChange",
        "change .reason_checkbox": "_onReasonChange",
    },

    start() {
        this.currentStep = 0;
        this.animating = false;

        this.$fieldsets = this.$("fieldset");
        this.$progressItems = this.$("#progressbar li");

        this._showStep(this.currentStep, false);

        return this._super(...arguments);
    },

    // ================================================================
    // NAVEGACIÓN
    // ================================================================

    _onNext(ev) {
        ev.preventDefault();

        if (this.animating) {
            return;
        }

        if (this.currentStep >= this.$fieldsets.length - 1) {
            return;
        }

        if (!this._validateCurrentStep()) {
            return;
        }
        this._goToStep(this.currentStep + 1, "next");
    },

    _validateCurrentStep() {
        const $fieldset = this.$fieldsets.eq(this.currentStep);

        if (!$fieldset.length) {
            return true;
        }

        const fieldset = $fieldset[0];

        // Buscar campos requeridos
        const requiredFields = fieldset.querySelectorAll(
            "input[required], select[required], textarea[required]"
        );

        for (const field of requiredFields) {

            if (!field.checkValidity()) {
                field.reportValidity();

                return false;
            }
        }

        return true;
    },

    _onPrevious(ev) {
        ev.preventDefault();

        if (this.animating) {
            return;
        }

        if (this.currentStep <= 0) {
            return;
        }

        this._goToStep(this.currentStep - 1, "previous");
    },

    _goToStep(newStep, direction) {
        const currentStep = this.currentStep;

        const $current = this.$fieldsets.eq(currentStep);
        const $next = this.$fieldsets.eq(newStep);

        if (!$current.length || !$next.length) {
            return;
        }

        this.animating = true;

        // Mostrar el siguiente fieldset
        $next.show();

        // Posición inicial
        if (direction === "next") {
            $next.css({
                left: "50%",
                opacity: 0,
                transform: "scale(1)",
                position: "absolute",
            });
        } else {
            $next.css({
                left: "0",
                opacity: 0,
                transform: "scale(0.8)",
                position: "absolute",
            });
        }

        // Forzar reflow antes de activar la transición
        $next[0].offsetHeight;

        // Activar transición CSS
        $current.css({
            transition: "opacity 0.8s ease-in-out, transform 0.8s ease-in-out",
        });

        $next.css({
            transition: "left 0.8s ease-in-out, opacity 0.8s ease-in-out, transform 0.8s ease-in-out",
        });

        if (direction === "next") {
            $current.css({
                opacity: 0,
                transform: "scale(0.8)",
            });

            $next.css({
                left: "0",
                opacity: 1,
                transform: "scale(1)",
            });
        } else {
            $current.css({
                opacity: 0,
                left: "50%",
            });

            $next.css({
                left: "0",
                opacity: 1,
                transform: "scale(1)",
            });
        }

        window.setTimeout(() => {
            $current.hide();

            $current.css({
                transition: "",
                transform: "",
                left: "",
                opacity: "",
                position: "",
            });

            $next.css({
                transition: "",
                transform: "",
                left: "",
                opacity: "",
                position: "",
            });

            this.currentStep = newStep;

            this._updateProgress();

            this.animating = false;
        }, 800);
    },

    _showStep(step, animate = true) {
        this.$fieldsets.hide();

        const $fieldset = this.$fieldsets.eq(step);

        if (!$fieldset.length) {
            return;
        }

        $fieldset.show();

        if (!animate) {
            $fieldset.css({
                opacity: 1,
                transform: "scale(1)",
                left: "0",
                position: "relative",
            });
        }

        this._updateProgress();
    },

    _updateProgress() {
        this.$progressItems.each((index, element) => {
            $(element).toggleClass("active", index <= this.currentStep);
        });
    },

    // ================================================================
    // TIPO DE RESPUESTA
    // ================================================================

    _onDeliveryTypeChange(ev) {
        const value = ev.currentTarget.value;

        const $email = this.$("#hidden_email");
        const $phone = this.$("#hidden_phone");

        $email.hide();
        $phone.hide();

        if (value === "email") {
            $email.show();
        }

        if (value === "phone") {
            $phone.show();
        }
    },

    // ================================================================
    // MOTIVOS
    // ================================================================

    _onReasonChange(ev) {
        const checked = this.$(".reason_checkbox:checked");

        if (checked.length > 2) {
            ev.currentTarget.checked = false;
        }
    },


});