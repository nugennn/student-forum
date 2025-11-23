function openInbox() {
    // getting = document.getElementsByTagName("myDiv2");
    gettingOpen = document.getElementsByTagName("myDiv");
    gettingOpen[0].classList.toggle("active");

    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    gettingAchieveOpen = document.getElementsByTagName("reviewDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }



    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    // Mark all notifications as read when inbox is opened
    markNotificationsAsRead();
}


function openAchievementInbox() {
    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    gettingAchieveOpen[0].classList.toggle("active");

    gettingAchieveOpen = document.getElementsByTagName("myDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }

    gettingAchieveOpen = document.getElementsByTagName("reviewDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    // Mark all achievements as read when inbox is opened
    markAchievementsAsRead();
}


function openReviewInbox() {
    gettingReviewOpen = document.getElementsByTagName("reviewDiv");
    gettingReviewOpen[0].classList.toggle("active");


    gettingAchieveOpen = document.getElementsByTagName("acvhieveDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }

    gettingAchieveOpen = document.getElementsByTagName("myDiv");
    if (gettingAchieveOpen[0].classList.contains("active")) {
        // alert("Achievements Inbox Panel is Open");
        gettingAchieveOpen[0].classList.toggle("active");
    }


    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }

    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    }



}


    $('._important, .myInboxSVGOuter').click(function() {
    var $this = $('.myInboxSVG');
    var forBackground = $('.myInboxSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});


    $('._positive, .achieveSVGOuter').click(function() {
    var $this = $('.achieveSVG');
    var forBackground = $('.achieveSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});


    $('._review, .reviewSVGOuter').click(function() {
    var $this = $('.reviewSVG');
    var forBackground = $('.reviewSVGOuter');

    if ($this.hasClass('fillTheSVG')) {
        $this.removeClass('fillTheSVG');
        forBackground.removeClass('forBackgroundClass');
    } else {
        $this.addClass('fillTheSVG');
        // alert("Third ")
        forBackground.addClass('forBackgroundClass');
    }
});

// Function to mark all notifications as read
function markNotificationsAsRead() {
    $.ajax({
        url: '/notification/read_All_Notifications/',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(response) {
            // Remove the notification badge
            $('.button__badge').fadeOut(300, function() {
                $(this).remove();
            });
            // Update the unread count
            $('.js-unread-count._important').text('0');
        },
        error: function(error) {
            console.log('Error marking notifications as read:', error);
        }
    });
}

// Function to mark all achievements as read
function markAchievementsAsRead() {
    $.ajax({
        url: '/notification/read_All_Priv_Notifications/',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(response) {
            // Remove the reputation badge
            $('.unseen-reputation').fadeOut(300, function() {
                $(this).remove();
            });
            // Update the unread count
            $('.js-unread-count._positive').text('+0');
        },
        error: function(error) {
            console.log('Error marking achievements as read:', error);
        }
    });
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

