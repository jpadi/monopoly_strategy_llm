"""Normative inline file envelope markers — must match docs/llm_platform/file_attachment_standard.md."""


class SpecificationAttachmentEnvelope:
    BEGIN = "--- BEGIN ATTACHED FILE: {path} ---"
    END = "--- END ATTACHED FILE: {path} ---"
    ATTACHED_FILES_HEADING = "## Attached specification files"

    @classmethod
    def beginMarker(cls, relativePath: str) -> str:
        return cls.BEGIN.format(path=relativePath)

    @classmethod
    def endMarker(cls, relativePath: str) -> str:
        return cls.END.format(path=relativePath)
