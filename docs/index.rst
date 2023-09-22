Welcome to the RCTab CLI documentation!
=======================================

This CLI can be used to request administrator access and can be used by admins to

* Add subscriptions to the Research Compute Billing System.
* Approve credits for a subscription.
  Approved credits are ring fenced for a subscription but can not be spent until they are allocated.
* Allocate credits (that have already been approved) to a subscription.
  They can now be spent.
* Check all the approvals and allocations made for a subscription.
* Get a summary of all the approvals, allocations and costs for all subscriptions.

The CLI can't be used to

* Create subscriptions on Azure.
  They must be created through the Azure portal and then added to the RCTab with the ``rctab sub add`` command.
* Add users to a subscription.
  Do this by other means such as through the Azure portal or with the Azure CLI.

..
    .. subprojecttoctree::
       :maxdepth: 2
       :caption: Contents:

.. toctree::
   :maxdepth: 2
   :caption: External Links
   :glob:
   :hidden:

   RCTab docs home <https://rctab.readthedocs.io/en/latest/>

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:
   :glob:

   Home <self>
   content/*

.. autosummary::
   :toctree: _autosummary
   :recursive:
   :caption: Docstrings

   rctab_cli


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
