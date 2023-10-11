======================
Sample
======================

This is a demo site for, generated as part of
`Sphinx Themes Gallery <https://sphinx-themes.org>`_.

.. important::

    This sample documentation was generated on |today|, and is rebuilt weekly.


Module contents
==========

.. automodule:: ecs.

1. Install this theme:

2. Set the following in your existing Sphinx documentation's ``conf.py`` file:

3. Build your Sphinx documentation with the new theme! [1]_


Documentation
=============


Exploration
===========

The section contains pages that contains basically
everything that you can with Sphinx "out-of-the-box".

.. toctree::
    :titlesonly:

Browsing through that section should give you a good idea of how stuff looks
in this theme.


Navigation
==========

This is the most important part of a documentation theme. If you like
the general look of the theme, please make sure that it is possible to
easily navigate through this sample documentation.

Ideally, the pages listed below should also be reachable via links
somewhere else on this page (like the sidebar, or a topbar). If they are
not, then this theme might need additional configuration to provide the
sort of site navigation that's necessary for "real" documentation.

.. toctree::
    :caption: This is a caption
    :titlesonly:

.. toctree::
    :hidden:
    :caption: Additional "hidden" Pages


Some pages like are declared in a "hidden"
toctree, and thus would not be visible above. However, they are still a
part of the overall site hierarchy and some themes may choose to present
them to the user in the site navigation.

-----

.. [1] If you hit an error while building documentation with a new theme,
    it is likely due to some theme-specific configuration in the ``conf.py``
    file of that documentation. These are usually ``html_sidebars``,
    ``html_theme_path`` or ``html_theme_config``. Unsetting those will likely
    allow the build to proceed.