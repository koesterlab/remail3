from sqlmodel import Session, select

from remail.models.settings import Settings
from remail.utils.session_management import session


class SettingsService:
    @staticmethod
    @session
    def __init_settings(self, session: Session) -> Settings:
        """
        Creates new settings row in db

        Returns:
            The settings row (either existing or newly created).
        """
        default_settings = Settings()
        session.add(default_settings)
        session.commit()
        session.refresh(default_settings)
        return default_settings

    @session
    def load_settings(self, session: Session) -> Settings:
        """
        Load settings with lowest id.

        Returns:
            Settings object (new or existing)
        """
        while True:
            settings = session.exec(select(Settings).order_by(Settings.id)).first()  # type:ignore
            if settings:
                return settings
            self.__init_settings(session)

    @session
    def save_settings(
        self,
        settings: Settings,
        session: Session,
    ) -> None:
        """
        Update settings for id=1.

        Args:
            settings: Settings object, can be from another db session
            session: Database session
        """
        settings.id = 1
        db_obj = self.load_settings()
        if db_obj:
            session.merge(settings)
        else:
            session.add(settings)
        session.commit()
        session.refresh(settings)
