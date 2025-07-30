// WhatsApp Widget Customizer
class WhatsAppWidgetCustomizer {
    constructor(config = {}) {
        this.config = {
            position: config.position || 'bottom-right',
            size: config.size || 60,
            backgroundColor: config.backgroundColor || '#25D366',
            hoverColor: config.hoverColor || '#128C7E',
            borderRadius: config.borderRadius || '50%',
            shadow: config.shadow || '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: config.zIndex || 9999,
            margin: config.margin || 20,
            animation: config.animation || true,
            showTooltip: config.showTooltip || false,
            tooltipText: config.tooltipText || 'Chat with us on WhatsApp',
            customIcon: config.customIcon || null
        };
        
        this.widget = null;
        this.tooltip = null;
    }

    create(phoneNumber, initialMessage) {
        if (this.widget) {
            this.remove();
        }

        // Create main widget container
        this.widget = document.createElement('div');
        this.widget.id = 'whatsapp-widget-custom';
        this.widget.style.cssText = this.getWidgetStyles();
        
        // Create widget button
        const button = document.createElement('div');
        button.style.cssText = this.getButtonStyles();
        button.innerHTML = this.getIconHTML();
        
        // Add hover effects
        button.addEventListener('mouseenter', () => {
            if (this.config.animation) {
                button.style.transform = 'scale(1.1)';
                button.style.backgroundColor = this.config.hoverColor;
            }
            if (this.config.showTooltip && this.tooltip) {
                this.tooltip.style.opacity = '1';
                this.tooltip.style.visibility = 'visible';
            }
        });
        
        button.addEventListener('mouseleave', () => {
            if (this.config.animation) {
                button.style.transform = 'scale(1)';
                button.style.backgroundColor = this.config.backgroundColor;
            }
            if (this.config.showTooltip && this.tooltip) {
                this.tooltip.style.opacity = '0';
                this.tooltip.style.visibility = 'hidden';
            }
        });
        
        // Add click handler
        button.addEventListener('click', () => {
            this.openWhatsApp(phoneNumber, initialMessage);
        });
        
        this.widget.appendChild(button);
        
        // Create tooltip if enabled
        if (this.config.showTooltip) {
            this.createTooltip();
        }
        
        // Add to page
        document.body.appendChild(this.widget);
        
        // Add entrance animation
        if (this.config.animation) {
            setTimeout(() => {
                this.widget.style.opacity = '1';
                this.widget.style.transform = 'scale(1)';
            }, 100);
        }
    }

    getWidgetStyles() {
        const positions = this.getPositionStyles();
        return `
            position: fixed;
            ${positions}
            z-index: ${this.config.zIndex};
            opacity: ${this.config.animation ? '0' : '1'};
            transform: ${this.config.animation ? 'scale(0.8)' : 'scale(1)'};
            transition: all 0.3s ease;
        `;
    }

    getButtonStyles() {
        return `
            width: ${this.config.size}px;
            height: ${this.config.size}px;
            background-color: ${this.config.backgroundColor};
            border-radius: ${this.config.borderRadius};
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: ${this.config.shadow};
            transition: all 0.3s ease;
            border: none;
            outline: none;
        `;
    }

    getPositionStyles() {
        const margin = this.config.margin;
        switch (this.config.position) {
            case 'bottom-left':
                return `bottom: ${margin}px; left: ${margin}px;`;
            case 'bottom-right':
                return `bottom: ${margin}px; right: ${margin}px;`;
            case 'top-left':
                return `top: ${margin}px; left: ${margin}px;`;
            case 'top-right':
                return `top: ${margin}px; right: ${margin}px;`;
            case 'center-left':
                return `top: 50%; left: ${margin}px; transform: translateY(-50%);`;
            case 'center-right':
                return `top: 50%; right: ${margin}px; transform: translateY(-50%);`;
            default:
                return `bottom: ${margin}px; right: ${margin}px;`;
        }
    }

    getIconHTML() {
        if (this.config.customIcon) {
            return this.config.customIcon;
        }
        
        const iconSize = Math.floor(this.config.size * 0.5);
        return `
            <svg width="${iconSize}" height="${iconSize}" viewBox="0 0 24 24" fill="white">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
            </svg>
        `;
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.textContent = this.config.tooltipText;
        this.tooltip.style.cssText = `
            position: absolute;
            background-color: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: ${this.config.zIndex + 1};
            ${this.getTooltipPosition()}
        `;
        
        this.widget.appendChild(this.tooltip);
    }

    getTooltipPosition() {
        const offset = 10;
        switch (this.config.position) {
            case 'bottom-left':
            case 'bottom-right':
                return `bottom: ${this.config.size + offset}px; right: 0;`;
            case 'top-left':
            case 'top-right':
                return `top: ${this.config.size + offset}px; right: 0;`;
            case 'center-left':
                return `right: ${this.config.size + offset}px; top: 50%; transform: translateY(-50%);`;
            case 'center-right':
                return `left: ${this.config.size + offset}px; top: 50%; transform: translateY(-50%);`;
            default:
                return `bottom: ${this.config.size + offset}px; right: 0;`;
        }
    }

    openWhatsApp(phoneNumber, initialMessage) {
        const cleanPhoneNumber = phoneNumber.replace(/[^0-9]/g, '');
        const encodedMessage = encodeURIComponent(initialMessage);
        const whatsappUrl = `https://wa.me/${cleanPhoneNumber}?text=${encodedMessage}`;
        
        // Add click animation
        if (this.config.animation && this.widget) {
            const button = this.widget.querySelector('div');
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1.1)';
            }, 100);
        }
        
        // Open WhatsApp
        window.open(whatsappUrl, '_blank');
    }

    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        if (this.widget) {
            // Re-create widget with new config
            const phoneNumber = this.widget.dataset.phoneNumber;
            const initialMessage = this.widget.dataset.initialMessage;
            if (phoneNumber && initialMessage) {
                this.create(phoneNumber, initialMessage);
            }
        }
    }

    remove() {
        if (this.widget) {
            this.widget.remove();
            this.widget = null;
            this.tooltip = null;
        }
    }

    hide() {
        if (this.widget) {
            this.widget.style.display = 'none';
        }
    }

    show() {
        if (this.widget) {
            this.widget.style.display = 'block';
        }
    }
}

// Export for use in other scripts
window.WhatsAppWidgetCustomizer = WhatsAppWidgetCustomizer;