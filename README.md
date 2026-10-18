# EV-ES Cloud for Home Assistant

This is a local, read-only Home Assistant custom integration. EV-BPM connects
only to EV-ES Cloud over MQTT/TLS. Home Assistant then reads the latest device
telemetry from Cloud over HTTPS every 15 seconds; it never receives the
device MQTT username, MQTT password, pairing key, or command key.

## Install through HACS (recommended)

The integration is prepared as a HACS repository. Publish the contents of
this directory as one public GitHub repository, for example
`EV-ES/eves-cloud-home-assistant`. HACS supports public GitHub repositories;
it does not install integrations from a Cloud URL or GitLab repository.

After publishing, place this one-click link on the EV-ES Cloud page, replacing
the example owner and repository with the actual GitHub values:

    https://my.home-assistant.io/redirect/hacs_repository/?owner=EV-ES&repository=eves-cloud-home-assistant&category=integration

Opening it from a phone or computer connected to Home Assistant opens the
EV-ES Cloud repository in HACS. The user selects Download, restarts Home
Assistant, then opens Settings, Devices & services, Add integration and selects
EV-ES Cloud. HACS will also offer future updates without copying files again.

## Manual install

1. Run migrations/20261102_cloud_home_assistant_tokens.sql once in the Cloud database.
2. Deploy cloud/home-assistant-api.php with the normal Cloud PHP files. It must
   be available at https://ev-es.pl/Cloud/home-assistant-api.php.
3. Copy the entire custom_components/eves_cloud directory into the
   custom_components directory of Home Assistant. On a typical HA OS or Home
   Assistant Container installation the destination is:

   /config/custom_components/eves_cloud/

4. Restart Home Assistant.
5. In Home Assistant open Settings, Devices & services, Add integration,
   select EV-ES Cloud, and enter:

   - Cloud URL: https://ev-es.pl/Cloud
   - the EV-ES Cloud account e-mail
   - the EV-ES Cloud password

The password is sent once over HTTPS to obtain a separate 90-day, read-only
token. The integration stores that token, not the password. Changing or
resetting the Cloud password invalidates the token automatically. Setting up a
new Home Assistant integration for the same account replaces the old token.

Administrator accounts are intentionally not accepted by this integration, so
Home Assistant cannot bypass administrator MFA. Use a normal Cloud user
account that has access to the desired devices. Shared devices are included.

## Entities

Each assigned EV-BPM becomes one Home Assistant device with sensors for SOC,
SOH, power, current, pack/cell voltages, temperature, cycles, current limits,
states and error counts. Binary sensors report online state, battery enabled
state, balancing and contactors. Device-level attributes contain the raw
states, group, last-seen time and error lists.

The first release is deliberately read-only. It does not send Enable, Disable,
Reset or configuration commands through Home Assistant.
