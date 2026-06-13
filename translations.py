# UI translations for HomeGridPilot.


TRANSLATIONS = {
    "de": {
        # language switcher
        "language": "Sprache",
        "lang_de": "Deutsch",
        "lang_en": "English",

        # login page
        "login_title": "Anmelden",
        "login_brand_sub": "Smart Home Steuerung",
        "login_welcome": "Willkommen zurück",
        "login_instructions": "Melde dich an, um deine Geräte zu steuern.",
        "username": "Benutzername",
        "password": "Passwort",
        "login_button": "Anmelden",
        "login_button_loading": "Anmelden…",
        "login_failed": "Anmeldung fehlgeschlagen",
        "default_credentials": "Standard-Zugangsdaten",

        # sidebar / nav
        "nav_overview": "Übersicht",
        "nav_dashboard": "Dashboard",
        "nav_analytics": "Auswertung",
        "nav_management": "Verwaltung",
        "nav_devices": "Geräte",
        "nav_settings": "Einstellungen",
        "administrator": "Administrator",
        "logout": "Abmelden",

        # topbar
        "refresh": "Aktualisieren",
        "add_device": "+ Gerät hinzufügen",

        # view titles / subtitles
        "view_dashboard_title": "Dashboard",
        "view_dashboard_subtitle": "Übersicht aller verbundenen Geräte",
        "view_analytics_title": "Auswertung",
        "view_analytics_subtitle": "Detaillierter Verbrauchsverlauf deiner Geräte",
        "view_devices_title": "Geräte",
        "view_devices_subtitle": "Verwaltung aller eingebundenen Geräte",
        "view_settings_title": "Einstellungen",
        "view_settings_subtitle": "Dashboard-Konfiguration",

        # dashboard summary cards
        "total_devices": "Geräte gesamt",
        "units": "Stk.",
        "online": "Online",
        "current_power": "Aktuelle Leistung",
        "energy_today": "Energie heute",
        "current_price": "Strompreis aktuell",
        "pv_production": "PV-Erzeugung",

        # price chart
        "price_chart_title": "Strompreis heute (aWattar Day-Ahead)",
        "price_chart_subtitle": "Aktuelle Stunde hervorgehoben · inkl. Aufschlag, falls in den Einstellungen hinterlegt",
        "price_unavailable": "Preisdaten nicht verfügbar",
        "hour_label": "Stunde {hour}",

        # my devices / empty states
        "my_devices": "Meine Geräte",
        "no_devices_title": "Noch keine Geräte",
        "no_devices_text": "Füge dein erstes Gerät hinzu, um es hier zu überwachen und zu steuern.",
        "load_demo": "Demo-Daten laden",
        "no_data_title": "Keine Daten vorhanden",
        "no_data_text": "Füge Geräte hinzu und lass sie einige Minuten laufen, um Verbrauchsdiagramme zu sehen.",
        "no_data_text_short": "Füge Geräte hinzu, um Diagramme zu sehen.",

        # devices list view
        "connected_devices": "Verbundene Geräte",
        "no_devices": "Keine Geräte vorhanden",

        # settings - general
        "settings_general": "Allgemein",
        "refresh_interval": "Aktualisierungsintervall",
        "refresh_interval_desc": "Wie oft Gerätedaten abgerufen werden",
        "sec_5": "5 Sek.",
        "sec_10": "10 Sek.",
        "sec_30": "30 Sek.",
        "sec_60": "60 Sek.",
        "change_password": "Passwort ändern",
        "change_password_desc": "Zugangspasswort für dieses Dashboard",
        "change": "Ändern",
        "language_desc": "Sprache der Benutzeroberfläche",

        # settings - automation
        "settings_automation": "Automatisierung & Strompreis",
        "automation_enabled": "Automatisierung aktiv",
        "automation_enabled_desc": "Globaler Schalter – schaltet Geräte gemäß ihren Regeln (Preis/PV-Überschuss)",
        "check_interval": "Prüfintervall",
        "check_interval_desc": "Wie oft Preis & PV geprüft und Geräte geschaltet werden",
        "min_1": "1 Min.",
        "min_5": "5 Min.",
        "min_10": "10 Min.",
        "min_15": "15 Min.",
        "price_markup": "Preisaufschlag",
        "price_markup_desc": "Wird auf den aWattar-Spotpreis addiert (Steuern, Netzgebühren, Marge), in ct/kWh",
        "check_now": "Jetzt prüfen",
        "check_now_desc": "Automatisierung sofort einmal für alle Geräte ausführen",
        "run": "▶ Ausführen",

        # settings - automation log
        "automation_log_title": "Automatisierungs-Protokoll",
        "automation_log_empty": "Noch keine Aktionen protokolliert.",

        # settings - info
        "info": "Info",
        "version": "Version",
        "supported_interfaces": "Unterstützte Schnittstellen",

        # add device modal
        "add_device_title": "Gerät hinzufügen",
        "add_device_desc": "Gib die IP-Adresse deines Geräts ein. Es muss im selben Netzwerk erreichbar sein.",
        "device_name": "Gerätename",
        "device_name_placeholder": "z. B. Wohnzimmer Steckdose",
        "ip_address": "IP-Adresse",
        "interface": "Schnittstelle",
        "interface_shelly": "Shelly (Gen1 / Gen2 / Gen3)",
        "interface_tasmota": "Tasmota",
        "interface_tplink": "TP-Link Kasa / Tapo",
        "device_type": "Gerätetyp",
        "type_plug": "Plug / Steckdose",
        "type_relay": "Relais",
        "type_dimmer": "Dimmer",
        "type_em": "Energiemesser",
        "type_pv": "PV-Anlage / Wechselrichter",
        "cancel": "Abbrechen",
        "add": "Hinzufügen",

        # chart modal
        "power_history": "Leistungsverlauf",
        "close": "Schließen",
        "power_label": "Leistung (W)",
        "chart_modal_sub": "IP: {ip} · Aktuell: {power} W",

        # automation modal
        "automation": "Automatisierung",
        "automation_for_device": "Regeln für „{name}“ – wird automatisch ein-/ausgeschaltet, solange die Automatisierung aktiv ist.",
        "automation_device_enabled": "Automatisierung für dieses Gerät aktiv",
        "auto_price_label": "Bei niedrigem Strompreis einschalten",
        "max_price": "Maximalpreis (ct/kWh)",
        "auto_pv_label": "Bei PV-Überschuss einschalten",
        "required_surplus": "Benötigter Überschuss (W)",
        "logic_label": "Verknüpfung der Bedingungen",
        "logic_or_option": "ODER – eine Bedingung reicht",
        "logic_and_option": "UND – beide Bedingungen nötig",
        "priority_label": "Priorität bei PV-Überschuss (1 = wird zuerst versorgt)",
        "save": "Speichern",

        # device card / dynamic JS
        "voltage": "Spannung",
        "current": "Strom",
        "energy": "Energie",
        "turn_off": "Ausschalten",
        "turn_on": "Einschalten",
        "on": "Ein",
        "off": "Aus",
        "history": "Verlauf",
        "remove": "Entfernen",
        "automation_on": "Automatik: An",
        "automation_off": "Automatik",

        # analytics charts
        "power_distribution": "Leistungsverteilung",
        "power_distribution_sub": "Aktuelle Watt-Verteilung je Gerät",
        "total_power": "Gesamtleistung (letzte Messungen)",
        "total_power_sub": "Summe aller Geräte",
        "consumption_per_device": "Verbrauch je Gerät",
        "consumption_per_device_sub": "Leistungsverlauf der letzten Messungen",
        "total_w_label": "Gesamt W",

        # toasts
        "automation_saved": "Automatisierung gespeichert",
        "save_error": "Fehler beim Speichern",
        "turned_on": "Eingeschaltet",
        "turned_off": "Ausgeschaltet",
        "action_on": "eingeschaltet",
        "action_off": "ausgeschaltet",
        "error": "Fehler",
        "please_enter_ip": "Bitte IP-Adresse eingeben",
        "device_added": "Gerät hinzugefügt",
        "confirm_delete_device": "Gerät wirklich entfernen?",
        "device_removed": "Gerät entfernt",
        "demo_devices_loaded": "{count} Demo-Geräte geladen",
        "demo_devices_exist": "Demo-Geräte bereits vorhanden",
        "interval_updated": "Intervall aktualisiert",
        "automation_settings_saved": "Automatisierungseinstellungen gespeichert",
        "automation_run": "Automatisierung ausgeführt",

        # backend errors / defaults
        "default_device_name": "Smart-Gerät",
        "too_many_attempts": "Zu viele Fehlversuche, bitte später erneut versuchen",
        "invalid_credentials": "Ungültiger Benutzername oder Passwort",
        "ip_required": "IP-Adresse erforderlich",
        "not_found": "Nicht gefunden",
        "device_unreachable": "Gerät nicht erreichbar",
        "unauthorized": "Nicht angemeldet",

        # automation log reason formatting
        "automation_reason_price": "Preis {value:.2f} ct/kWh {cmp} {threshold:.2f} ct/kWh",
        "automation_reason_pv": "PV-Überschuss {value:.0f} W {cmp} {threshold:.0f} W",
        "joiner_and": " UND ",
        "joiner_or": " ODER ",

        # demo devices
        "demo_living_room_lamp": "Wohnzimmer Lampe",
        "demo_office_pc": "Büro PC",
        "demo_fridge": "Kühlschrank",
        "demo_pv_inverter": "PV-Wechselrichter",
    },
    "en": {
        # language switcher
        "language": "Language",
        "lang_de": "Deutsch",
        "lang_en": "English",

        # login page
        "login_title": "Sign In",
        "login_brand_sub": "Smart Home Control",
        "login_welcome": "Welcome back",
        "login_instructions": "Sign in to control your devices.",
        "username": "Username",
        "password": "Password",
        "login_button": "Sign in",
        "login_button_loading": "Signing in…",
        "login_failed": "Sign in failed",
        "default_credentials": "Default credentials",

        # sidebar / nav
        "nav_overview": "Overview",
        "nav_dashboard": "Dashboard",
        "nav_analytics": "Analytics",
        "nav_management": "Management",
        "nav_devices": "Devices",
        "nav_settings": "Settings",
        "administrator": "Administrator",
        "logout": "Log out",

        # topbar
        "refresh": "Refresh",
        "add_device": "+ Add device",

        # view titles / subtitles
        "view_dashboard_title": "Dashboard",
        "view_dashboard_subtitle": "Overview of all connected devices",
        "view_analytics_title": "Analytics",
        "view_analytics_subtitle": "Detailed consumption history of your devices",
        "view_devices_title": "Devices",
        "view_devices_subtitle": "Manage all connected devices",
        "view_settings_title": "Settings",
        "view_settings_subtitle": "Dashboard configuration",

        # dashboard summary cards
        "total_devices": "Total devices",
        "units": "units",
        "online": "Online",
        "current_power": "Current power",
        "energy_today": "Energy today",
        "current_price": "Current electricity price",
        "pv_production": "PV production",

        # price chart
        "price_chart_title": "Electricity price today (aWattar Day-Ahead)",
        "price_chart_subtitle": "Current hour highlighted · incl. markup if configured in settings",
        "price_unavailable": "Price data unavailable",
        "hour_label": "Hour {hour}",

        # my devices / empty states
        "my_devices": "My devices",
        "no_devices_title": "No devices yet",
        "no_devices_text": "Add your first device to monitor and control it here.",
        "load_demo": "Load demo data",
        "no_data_title": "No data available",
        "no_data_text": "Add devices and let them run for a few minutes to see consumption charts.",
        "no_data_text_short": "Add devices to see charts.",

        # devices list view
        "connected_devices": "Connected devices",
        "no_devices": "No devices available",

        # settings - general
        "settings_general": "General",
        "refresh_interval": "Refresh interval",
        "refresh_interval_desc": "How often device data is fetched",
        "sec_5": "5 sec",
        "sec_10": "10 sec",
        "sec_30": "30 sec",
        "sec_60": "60 sec",
        "change_password": "Change password",
        "change_password_desc": "Access password for this dashboard",
        "change": "Change",
        "language_desc": "Language of the user interface",

        # settings - automation
        "settings_automation": "Automation & Electricity Price",
        "automation_enabled": "Automation active",
        "automation_enabled_desc": "Global switch – switches devices according to their rules (price/PV surplus)",
        "check_interval": "Check interval",
        "check_interval_desc": "How often price & PV are checked and devices are switched",
        "min_1": "1 min",
        "min_5": "5 min",
        "min_10": "10 min",
        "min_15": "15 min",
        "price_markup": "Price markup",
        "price_markup_desc": "Added to the aWattar spot price (taxes, grid fees, margin), in ct/kWh",
        "check_now": "Check now",
        "check_now_desc": "Run automation immediately once for all devices",
        "run": "▶ Run",

        # settings - automation log
        "automation_log_title": "Automation Log",
        "automation_log_empty": "No actions logged yet.",

        # settings - info
        "info": "Info",
        "version": "Version",
        "supported_interfaces": "Supported interfaces",

        # add device modal
        "add_device_title": "Add device",
        "add_device_desc": "Enter your device's IP address. It must be reachable on the same network.",
        "device_name": "Device name",
        "device_name_placeholder": "e.g. Living room socket",
        "ip_address": "IP address",
        "interface": "Interface",
        "interface_shelly": "Shelly (Gen1 / Gen2 / Gen3)",
        "interface_tasmota": "Tasmota",
        "interface_tplink": "TP-Link Kasa / Tapo",
        "device_type": "Device type",
        "type_plug": "Plug / Socket",
        "type_relay": "Relay",
        "type_dimmer": "Dimmer",
        "type_em": "Energy meter",
        "type_pv": "PV system / Inverter",
        "cancel": "Cancel",
        "add": "Add",

        # chart modal
        "power_history": "Power History",
        "close": "Close",
        "power_label": "Power (W)",
        "chart_modal_sub": "IP: {ip} · Current: {power} W",

        # automation modal
        "automation": "Automation",
        "automation_for_device": "Rules for “{name}” – will be switched on/off automatically as long as automation is active.",
        "automation_device_enabled": "Automation active for this device",
        "auto_price_label": "Turn on at low electricity price",
        "max_price": "Maximum price (ct/kWh)",
        "auto_pv_label": "Turn on at PV surplus",
        "required_surplus": "Required surplus (W)",
        "logic_label": "Condition logic",
        "logic_or_option": "OR – one condition is enough",
        "logic_and_option": "AND – both conditions required",
        "priority_label": "Priority for PV surplus (1 = served first)",
        "save": "Save",

        # device card / dynamic JS
        "voltage": "Voltage",
        "current": "Current",
        "energy": "Energy",
        "turn_off": "Turn off",
        "turn_on": "Turn on",
        "on": "On",
        "off": "Off",
        "history": "History",
        "remove": "Remove",
        "automation_on": "Automation: On",
        "automation_off": "Automation",

        # analytics charts
        "power_distribution": "Power Distribution",
        "power_distribution_sub": "Current watt distribution per device",
        "total_power": "Total Power (recent readings)",
        "total_power_sub": "Sum of all devices",
        "consumption_per_device": "Consumption per Device",
        "consumption_per_device_sub": "Power history of recent readings",
        "total_w_label": "Total W",

        # toasts
        "automation_saved": "Automation saved",
        "save_error": "Error saving",
        "turned_on": "Turned on",
        "turned_off": "Turned off",
        "action_on": "turned on",
        "action_off": "turned off",
        "error": "Error",
        "please_enter_ip": "Please enter an IP address",
        "device_added": "Device added",
        "confirm_delete_device": "Really remove this device?",
        "device_removed": "Device removed",
        "demo_devices_loaded": "{count} demo devices loaded",
        "demo_devices_exist": "Demo devices already exist",
        "interval_updated": "Interval updated",
        "automation_settings_saved": "Automation settings saved",
        "automation_run": "Automation executed",

        # backend errors / defaults
        "default_device_name": "Smart device",
        "too_many_attempts": "Too many failed attempts, please try again later",
        "invalid_credentials": "Invalid username or password",
        "ip_required": "IP address required",
        "not_found": "Not found",
        "device_unreachable": "Device unreachable",
        "unauthorized": "Unauthorized",

        # automation log reason formatting
        "automation_reason_price": "Price {value:.2f} ct/kWh {cmp} {threshold:.2f} ct/kWh",
        "automation_reason_pv": "PV surplus {value:.0f} W {cmp} {threshold:.0f} W",
        "joiner_and": " AND ",
        "joiner_or": " OR ",

        # demo devices
        "demo_living_room_lamp": "Living Room Lamp",
        "demo_office_pc": "Office PC",
        "demo_fridge": "Refrigerator",
        "demo_pv_inverter": "PV Inverter",
    },
}


def get_translations(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["de"])
