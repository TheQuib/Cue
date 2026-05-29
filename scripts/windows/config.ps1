# =============================================================================
# Cue Display Configuration
# Edit this file for your location before running any scripts.
# =============================================================================

# List each Cue display for this location.
# api_key must match the api_key set in that display's config.yml.
$displays = @(
    @{ name = "Main Hallway TV";    host = "192.168.1.101"; port = 5000; api_key = "changeme" }
    @{ name = "Office TV";          host = "192.168.1.102"; port = 5000; api_key = "changeme" }
    @{ name = "Conference Room TV"; host = "192.168.1.103"; port = 5000; api_key = "changeme" }
)
