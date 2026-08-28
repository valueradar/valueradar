# Site security rules

- Keep marketplace host allowlisting in the generator.
- Escape product content before inserting it into generated HTML.
- Do not store affiliate account credentials, API secrets or analytics credentials in repository files.
- Use GitHub encrypted secrets if future Actions need external API credentials.
- Keep third-party scripts minimal and intentional.
- Treat product URLs/data as untrusted input and validate before publishing.
