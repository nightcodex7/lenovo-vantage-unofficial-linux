#!/bin/bash

#Requirement: zenity, xinput, networkmanager, pulseaudio or pipewire-pulse
#Contributors: https://github.com/nightcodex7

ENABLE_FAN_MODE=1

VPC="/sys/bus/platform/devices/VPC2004\:*"

read_sysfs() {
    for f in $1; do
        if [ -f "$f" ]; then cat "$f" 2>/dev/null; return 0; fi
    done
    echo ""
}

get_power_mode_status() {
    local val=$(read_sysfs "/sys/firmware/acpi/platform_profile")
    [ -z "$val" ] && { echo "N/A"; return; }
    echo "$val" | awk '{
        if ($1 == "low-power") print "Quiet";
        else if ($1 == "balanced") print "Balanced";
        else if ($1 == "performance") print "Performance";
        else print "Unknown";
    }'
}

get_conservation_mode_status() {
    local val=$(read_sysfs "$VPC/conservation_mode")
    [ -z "$val" ] && { echo "N/A"; return; }
    echo "$val" | awk '{print ($1 == "1") ? "On" : "Off"}'
}

get_usb_charging_status() {
    local val=$(read_sysfs "$VPC/usb_charging")
    [ -z "$val" ] && { echo "N/A"; return; }
    echo "$val" | awk '{print ($1 == "1") ? "On" : "Off"}'
}

get_fan_mode_status() {
    local val=$(read_sysfs "$VPC/fan_mode")
    [ -z "$val" ] && { echo "N/A"; return; }
    echo "$val" | awk '{
        if ($1 == "133" || $1 == "0") print "Super Silent";
        else if ($1 == "1") print "Standard";
        else if ($1 == "2") print "Dust Cleaning";
        else if ($1 == "4") print "Efficient Thermal Dissipation";
        else print "Unknown (" $1 ")";
    }'
}

get_fn_lock_status() {
    local val=$(read_sysfs "$VPC/fn_lock")
    [ -z "$val" ] && { echo "N/A"; return; }
    echo "$val" | awk '{print ($1 == "1") ? "Off" : "On"}'
}

get_camera_status() {
    lsmod | grep -q 'uvcvideo' && echo "On" || echo "Off"
}

get_microphone_status() {
    pactl get-source-mute @DEFAULT_SOURCE@ | awk '{print ($2 == "yes") ? "Off (Muted)" : "On (Active)"}'
}

get_touchpad_status() {
    [ -z "$touchpad_id" ] && { echo "N/A"; return; }
    xinput --list-props "$touchpad_id" | grep "Device Enabled" | cut -d ':' -f2 | awk '{print ($1 == "1") ? "On" : "Off"}'
}

get_wifi_status() {
    nmcli radio wifi | awk '{print ($1 == "enabled") ? "On" : "Off"}'
}

show_submenu() {
    local title="$1"
    local status="$2"
    zenity --list --title "$title" --text "Status: $status" --column "Menu" "${@:3}"
}

show_submenu_on_off() {
    show_submenu "$1" "$2" "Enable" "Disable"
}

confirm_action() {
    zenity --question --title "Confirm Action" --text "Are you sure you want to apply this change?\n\nChanging this mode will modify system parameters directly."
}

main() {
    while :; do
        touchpad_id="$(xinput list | grep "Touchpad" | cut -d '=' -f2 | awk '{print $1}')"
        local options=()
        test -f /sys/firmware/acpi/platform_profile && options+=("Power Mode" "$(get_power_mode_status)")
        # For globs, we can't reliably use test -f directly without expanding, but this relies on the first match existing.
        # We will use ls to check if the path exists to be safer.
        ls $VPC/conservation_mode >/dev/null 2>&1 && options+=("Conservation Mode" "$(get_conservation_mode_status)")
        ls $VPC/usb_charging >/dev/null 2>&1 && options+=("Always-On USB" "$(get_usb_charging_status)")
        ls $VPC/fan_mode >/dev/null 2>&1 && test "$ENABLE_FAN_MODE" = 1 && options+=("Fan Mode" "$(get_fan_mode_status)")
        ls $VPC/fn_lock >/dev/null 2>&1 && options+=("FN Lock" "$(get_fn_lock_status)")
        modinfo -n uvcvideo >/dev/null 2>&1 && options+=("Camera" "$(get_camera_status)")
        which pactl >/dev/null 2>&1 && options+=("Microphone" "$(get_microphone_status)")
        test -n "$touchpad_id" && options+=("Touchpad" "$(get_touchpad_status)")
        which nmcli >/dev/null 2>&1 && options+=("WiFi" "$(get_wifi_status)")

        local height=$(( ${#options[@]} / 2 * 35 + 120 ))
        local menu="$(zenity --list --title "Lenovo Vantage v1.0.0" --text "Select function:" --column "Function" --column "Status" "${options[@]}" --height $height --width 350)"
        
        case "$menu" in
            "Power Mode")
                local submenu="$(show_submenu "Power Mode" "$(get_power_mode_status)" --height 250 --width 300 \
                    "Quiet" \
                    "Balanced" \
                    "Performance" \
                )"
                case "$submenu" in
                    "Quiet") echo "low-power" | pkexec tee /sys/firmware/acpi/platform_profile > /dev/null ;;
                    "Balanced") echo "balanced" | pkexec tee /sys/firmware/acpi/platform_profile > /dev/null ;;
                    "Performance") echo "performance" | pkexec tee /sys/firmware/acpi/platform_profile > /dev/null ;;
                esac
                ;;
            "Conservation Mode")
                local submenu="$(show_submenu_on_off "Conservation Mode" "$(get_conservation_mode_status)")"
                case "$submenu" in
                    "Enable") confirm_action && echo "1" | pkexec tee $VPC/conservation_mode >/dev/null ;;
                    "Disable") confirm_action && echo "0" | pkexec tee $VPC/conservation_mode >/dev/null ;;
                esac
                ;;
            "Always-On USB")
                local submenu="$(show_submenu_on_off "Always-On USB" "$(get_usb_charging_status)")"
                case "$submenu" in
                    "Enable") echo "1" | pkexec tee $VPC/usb_charging >/dev/null ;;
                    "Disable") echo "0" | pkexec tee $VPC/usb_charging >/dev/null ;;
                esac
                ;;
            "Fan Mode")
                local submenu="$(show_submenu "Fan Mode" "$(get_fan_mode_status)" --height 250 --width 300 \
                    "Super Silent" \
                    "Standard" \
                    "Dust Cleaning" \
                    "Efficient Thermal Dissipation" \
                )"
                case "$submenu" in
                    "Super Silent") confirm_action && echo "0" | pkexec tee $VPC/fan_mode >/dev/null ;;
                    "Standard") confirm_action && echo "1" | pkexec tee $VPC/fan_mode >/dev/null ;;
                    "Dust Cleaning") confirm_action && echo "2" | pkexec tee $VPC/fan_mode >/dev/null ;;
                    "Efficient Thermal Dissipation") confirm_action && echo "4" | pkexec tee $VPC/fan_mode >/dev/null ;;
                esac
                ;;
            "FN Lock")
                local submenu="$(show_submenu_on_off "FN Lock" "$(get_fn_lock_status)")"
                case "$submenu" in
                    "Enable") echo "0" | pkexec tee $VPC/fn_lock >/dev/null ;;
                    "Disable") echo "1" | pkexec tee $VPC/fn_lock >/dev/null ;;
                esac
                ;;
            "Camera")
                local submenu="$(show_submenu_on_off "Camera" "$(get_camera_status)")"
                case "$submenu" in
                    "Enable") pkexec modprobe uvcvideo ;;
                    "Disable") pkexec modprobe -r uvcvideo ;;
                esac
                ;;
            "Microphone")
                local submenu="$(show_submenu "Microphone" "$(get_microphone_status)" \
                    "On (Active)" \
                    "Off (Muted)" \
                )"
                case "$submenu" in
                    "On (Active)") pactl set-source-mute @DEFAULT_SOURCE@ 0 ;;
                    "Off (Muted)") pactl set-source-mute @DEFAULT_SOURCE@ 1 ;;
                esac
                ;;
            "Touchpad")
                local submenu="$(show_submenu_on_off "Touchpad" "$(get_touchpad_status)")"
                case "$submenu" in
                    "Enable") xinput enable "$touchpad_id" ;;
                    "Disable") xinput disable "$touchpad_id" ;;
                esac
                ;;
            "WiFi")
                local submenu="$(show_submenu_on_off "WiFi" "$(get_wifi_status)")"
                case "$submenu" in
                    "Enable") nmcli radio wifi on ;;
                    "Disable") nmcli radio wifi off ;;
                esac
                ;;
            *)
                break
                ;;
        esac
    done
}

main "$@"

