from tripadvisor import db
import logging

logger = logging.getLogger()

def get_success_status():
    return {"status": "success"}


def get_error_status():
    return {"status": "error"}


def save(row):
    try:
        db.session.add(row)
        db.session.commit()
        return get_success_status()

    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return get_error_status()


def update():
    try:
        db.session.commit()
        return get_success_status()
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return get_error_status()


def delete(row):
    try:
        db.session.delete(row)
        db.session.commit()
        return get_success_status()
        
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return get_error_status()