#Roadmap for initial development
# Introduction #

This page contains an outline of the features we need to implement for the first working version of the accounts app.

Items listed as done include unit tests.
# Details #

**Profile Section:**
> Allows People to edit their profile information.
> _Done:_
    * Edit profile
    * Change password
> _To Do:_
    * Replace stub templates with working templates
> _To Consider:_
    * As it is, the user can be given permission to edit their full profile, or be denied permission to edit it. Do we need attribute-specific permissions?


**Person admin section for account owner:**
> Allows account administrators to manage People.
> _Done:_
    * List, Create, Edit, Delete user.
> _To Do:_
    * Replace stub templates with working templates
    * Test form for adding roles to users


**Subscription level system:**
> Lets you define subscription levels which limit the
> amount of resources available to an account.

> I only have a rough idea of how this will work. My thought
> is that the developer should create a Subscription class which
> is able to check the amount of resources being used against the
> amount available for a particular subscription level.

> The Subscription class could then be set in django.settings,
> for access by middleware or decorators.

> _Done:_
> _To Do:_
    * Write SubscriptionBase class.
    * Write decorators or middleware to prohibit requests that would result in exceeding the resource limit.
    * Write templates.
    * Write template tags for displying content based on subscription level.
    * View: Show current subscription level
    * View: Show menu of all subscription levels.


**Free trial:**
> It looks like we can get this functionaliy without really
> writing any code. I've looked at several Automated Recurring
> Billing systems (AuthorizeNet, TrustCommerce, USAEpay). They
> all have a free trial system built in. Basically, you do the
> credit card transaction and they wait 30 days before billing.

> The other way involves tracking the free trial yourself, then
> asking the user for their credit card info after it expires. I've
> actually done this before. It's a huge pain in the neck. You have
> to handle lots of edge cases.


**Authentication System:**
> Handles person authentication.
> _Done:_
    * Login, logout, reset password
    * Allow or deny access to urls based on login status, role, or account (domain name)
> _To Do:_
    * Replace stub templates with working templates


**Payment gateway integration:**
> Sets up automatic recurring billing via credit card.

> We can easily make this modular, the developer can chose
> which gateway they want to use. I'll write code for integration
> with authorize.net, since that's the gateway I am using.

> _Done:_
> _To Do:_
    * Model: CreditCardTransaction Model
    * Lib: authorize.net module
    * View: Show current payment method
    * View: Cancel payment
    * View: Change payment method.
    * View: Upgrade/downgrade subscription level.

**Account Creation:**
> The process should look something like this:
    * User selects subscription level from menu of choices
    * User provides selects account subdomain, name, etc.
    * User provides login details for account administrator
    * User provides payment information, if paid subscription.
    * Redirects to new domain
    * User logs in

**Edit Account:**
> Account admin should be able to change account name,
> subdomain, etc.







