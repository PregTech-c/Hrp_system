var updateSuccess = function (response) {
    console.log(response);
    $('#notifUnreadCount').html(response.unread_count);
    var notification_box = $(nfBoxListClassSelector);
    var notifications = response.notifications;
    $.each(notifications, function (i, notification) {
        notification_box.prepend(notification.html);
    });
};
