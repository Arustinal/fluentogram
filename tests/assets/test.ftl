# Simple message
hello = Hello, world!

# Multiline value
multiline =
    This is a multiline message.
    It continues on multiple lines.

# Variables
welcome = Hello, { $name }!

# Attributes
button =
    .label = Send
    .accesskey = O

# Selectors
email-status =
    { $unreadCount ->
        [0] You have no new emails.
        [one] You have { $unreadCount } new email.
        [few] You have { $unreadCount } new emails.
       *[other] You have { $unreadCount } new emails.
    }

# Message reference
greeting = { hello } This is a phrase with another message.

# Selector by state
task-state =
    { $state ->
        [new] New task
        [in-progress] In progress
        [done] Done
       *[other] Unknown state
    }

# Function call (for formatting date/numbers)
formatted-date = Today: { DATETIME($date, month: "long", year: "numeric", day: "numeric") }

# Example with NUMBER and using parameters
score = You scored { NUMBER($points, minimumFractionDigits: 1) } points

# Example with nested messages
outer-message = Attachment: { inner-message }
inner-message = This is a nested message.

# Escaping curly braces
escaped = This is not a variable: {{ $notAVar }}

# Using terms (terms, starting with -)
-brand-name = Application X
about = Information about { -brand-name }

# Term attribute
-icon =
    .src = /images/icon.svg
    .alt = Icon

# Comments
# This is a regular comment
## This is a group comment
### This is a documenting comment

# Combination of everything
complex-message =
    Welcome, { $name }!
    Today { DATETIME($date, weekday: "long") }.
    You have { $unreadCount ->
        [0] no new emails.
        [one] one new email.
        [few] { $unreadCount } new emails.
       *[other] { $unreadCount } new emails.
    }
    Thank you for using { -brand-name }!