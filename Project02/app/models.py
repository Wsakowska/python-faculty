from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Tymczasowy user_loader — zostanie zastąpiony prawdziwym w commicie 3."""
    return None