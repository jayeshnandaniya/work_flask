from unittest.mock import patch
import datetime

patch('flask_jwt_extended.jwt_required', lambda x: x).start()

@patch('src.resources.notifications.models')
@patch('src.resources.notifications.request')
@patch('src.resources.notifications.db_session')
def test_notification_list_get(
        mock_db_session, mock_request,
        mock_model, app, notifications,
        model_notification, request_json):

    mock_request.args = {
        'only_read': True,
        'only_unread': False,
        'before': '2014-12-22T03:12:58.019077+00:00',
        'after': '2014-12-22T03:12:58.019077+00:00'
    }

    mock_model.Notification.return_value = model_notification
    mock_model.Notification.created_at = datetime.datetime.now()

    ( # Mock db_session.query().filter().filter().filter().filter().all()
        mock_db_session.query.return_value.
        filter.return_value.
        filter.return_value.
        filter.return_value.
        filter.return_value.
        all.return_value
    ) = [model_notification]

    notification_list = notifications.NotificationList()
    with app.test_request_context():
        notifications_list = notification_list.get()

    assert len(notifications_list) == 1
    assert notifications_list[0]['id'] == 8


@patch('src.resources.notifications.models')
@patch('src.resources.notifications.request')
@patch('src.resources.notifications.db_session')
def test_notification_put(
        mock_db_session, mock_request,
        mock_model, app, notifications,
        model_notification, request_json):

    mock_request.get_json.return_value = {
        'only_read': True,
        'only_unread': False,
        'is_read': True,
        'before': '2014-12-22T03:12:58.019077+00:00',
        'after': '2014-12-22T03:12:58.019077+00:00'
    }

    mock_model.Notification.return_value = model_notification
    mock_model.Notification.created_at = datetime.datetime.now()

    ( # Mock db_session.query().filter().filter().filter().filter().all()
        mock_db_session.
        query.return_value.
        filter.return_value.
        one_or_none.return_value
    ) = model_notification

    notification = notifications.Notification()
    with app.test_request_context():
        notification_dict = notification.put(8)

    assert isinstance(notification_dict, dict)
    assert notification_dict['id'] == 8
