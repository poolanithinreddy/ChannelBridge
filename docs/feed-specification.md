# ChannelBridge feed specification 1.0

This independent public teaching schema has no relationship to a commercial streaming platform. JSON uses `feed_version`; XML uses a `channelbridge_feed version="1.0"` root. Both require a fictional partner identifier and programs with identifiers, descriptive metadata, language, territory, artwork metadata, and availability windows. See `/schemas` and `/samples`.

Unsupported versions produce `SCHEMA_UNSUPPORTED`. XML parsing disables entities via `defusedxml`; URLs are validated but never fetched. Uploads are limited to 10 MiB.

