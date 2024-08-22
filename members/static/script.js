// Choose Department, reload page with new url and view
function updateForm(event) {
    event.preventDefault() // prevents form from submitting immediately
    const department = document.getElementById("department-select").value.toUpperCase() // gets value of textfield
    const url = '{% url "courses" "temp" %}'.replace('temp', department.replace(/[\s\\\/]/g, "%20")) // django url takes the current url and urlpatterns from urls.py
    window.location.href = url
}

// Note Functions
function showNote(event) {
    const innerCard =  event.target.previousElementSibling.firstElementChild
    const saveButton = event.target.previousElementSibling.lastElementChild
    const noteButton = event.target
    
    if (innerCard.style.maxHeight === '' || innerCard.style.maxHeight !== 'none') {
        innerCard.style.maxHeight = "none"
        innerCard.style.visibility = "visible"
        saveButton.style.visibility = "visible"
        noteButton.textContent = '- Close Notes'
    } else {
        innerCard.style.maxHeight = 0
        innerCard.style.visibility = "hidden"
        saveButton.style.visibility = "hidden"
        noteButton.textContent = '+ Add Notes'
    }
}

function saveNote(event) {
    var noteElement = (event instanceof PointerEvent) ? event.target : event  

    if (noteElement.textContent == 'Save') {
        noteElement.textContent = 'Saved!'
        noteElement.style.color = 'var(--main-color1)'

        setTimeout(function() {
            noteElement.textContent = 'Save'
            noteElement.style.color = 'var(--main-color2)'
        }, 3000)
    }
}


// JQUERY SAVE FUNCTIONS
function jquerySave(noteContent, courseID) {
    $.ajax({
        type: 'POST',
        url: '{% url "save_note" %}',
        data: {
            'note_content': noteContent,
            'course_id': courseID.trim(),
            'csrfmiddlewaretoken': '{{ csrf_token }}',
        },
    })
}

// Closest and find are jquery methods! Meaning i can only call them on $ (jquery) objects
$(document).ready(function() {
    $('.save-button').click(function() {
        event.preventDefault()

        var saveButton = $(this) // grabs the clicked button as an element
        var courseCard = saveButton.closest('.course-card') // closest travels up the DOM tree until it finds a matching value

        var noteContent = courseCard.find('.note-box').val() // find travels down the DOM tree
        var courseID = courseCard.find('.course-title.id').text()

        //Ajax stands for Asynchronus JAvacsript Xml, some cool async tpya stuff
        jquerySave(noteContent, courseID)
    })
})

// We use $(document).on('click') instead of $(document).click because 
//  .click only attaches event listeners to elements that already exist
//  in the DOM 
var $recentNoteBox
$(document).ready(function() {
    $(document).on('click', function(event) {
        // Save if current target is neither the most recent notebox or its save-button
        if (!$(event.target).is($recentNoteBox) && $recentNoteBox) {  
            const saveButton = $recentNoteBox.closest('.course-card').find('.save-button')
            if (!$(event.target).is(saveButton)) {
                var courseID = $recentNoteBox.closest('.course-card').find('.course-title.id').text()
                jquerySave($recentNoteBox.val(), courseID) // For some reason i need to use val() and not text()
                saveNote(saveButton[0])
                $recentNoteBox = ''
            }
        }
        
        if (event.target.className == 'note-box') {
            $recentNoteBox = $(event.target)
        }
    })
})


// Filter Functions
function openFilter(event) {
    var filterButton = document.getElementById('filter')
    var filterMenu = document.getElementById('filter-menu')
    
    //event.stopPropagation()
    var rect = filterButton.getBoundingClientRect()
    filterMenu.style.top = rect.bottom + 'px'
    filterMenu.style.left = rect.left + 'px'
    filterMenu.classList.toggle("hidden")
}

// Close the menus if clicking outside of it
document.addEventListener('click', function(event) {
    var filterButton = document.getElementById('filter')
    var filterMenu = document.getElementById('filter-menu') 

    if (!filterMenu.contains(event.target) && !filterButton.contains(event.target)) {
        filterMenu.classList.add('hidden')
    }

    var popupMenu = document.getElementById('popup-menu')
    if (!popupMenu.contains(event.target)) {
        popupMenu.classList.remove('active')
    }
})

function hideCards(event) {
    const noteBoxes = document.getElementsByClassName('note-box')
    for (let i = 0; i < noteBoxes.length; i++) {
        var noteBox = noteBoxes[i]
        var courseCard = noteBox.closest('.course-card')

        if (event.target.checked) {
            if (noteBox.textContent.trim() == '') {
                courseCard.classList.add('hidden')
            }
        } else {
            if (courseCard.classList.contains('hidden')) {
                courseCard.classList.remove('hidden')
            }
        }
    }
}

// Popup Functions
var lastTopPos
var lastLeftPos
$(function() { // $(document).ready shorthand!
    $('body').on('click', '.course-popup', function() {
        var $courseElement = $(this) // span course-popup element
        var courseName = $courseElement.text()

        $.ajax({
            url: '{% url "popup" %}',
            type: 'GET',
            data: {
                'course_id': courseName,
            },
            success: function(response) {
                $('#popup-menu').remove();
                var $popup = $('<div id="popup-menu"></div>').html(response.html)
                
                var offset = $courseElement.offset() // gets coords of element relative to document
                var topPos = offset.top + $courseElement.height() // top offset + the height of the text so window appears right below
                var leftPos = offset.left

                $('body').append($popup);
                
                if (!$courseElement.closest('#popup-menu').length) {
                    var popupWidth = $popup.outerWidth();
                    var rightEdge = leftPos + popupWidth;

                    var screenWidth = $(window).width()
                    if (rightEdge > screenWidth) { // if popup window is off of screen
                        leftPos = screenWidth - popupWidth - 10 // -10 for padding!
                    }

                    lastTopPos = topPos
                    lastLeftPos = leftPos
                } else {
                    topPos = lastTopPos
                    leftPos = lastLeftPos
                }
                
                
                $popup.css({
                    top: topPos,
                    left: leftPos
                })

                $popup.addClass('active');
            },
            error: function(xhr, status, error) {
                console.log("An error occurred: " + error);
            }
        })
    })
})