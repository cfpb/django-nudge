from distutils.core import setup


# Load in babel support, if available.
try:
    from babel.messages import frontend as babel
    cmdclass = {"compile_catalog": babel.compile_catalog,
                "extract_messages": babel.extract_messages,
                "init_catalog": babel.init_catalog,
                "update_catalog": babel.update_catalog,}
except ImportError:
    cmdclass = {}


setup(name="django-nudge",
      version="0.5.3",
      description="Use Nudge to (gently) push content between Django servers",
      author="Joshua Ruihley, Ross Karchner",
      author_email="joshua.ruihley@cfpb.gov",
      url="https://github.com/jroo/django-nudge",
      download_url="https://github.com/downloads/jroo/django-nudge/django-nudge-0.5.3.tar.gz",
      zip_safe=False,
      packages=["nudge", "nudge.demo", "nudge.management", "nudge.templatetags", "nudge.management.commands"],
      package_data = {"nudge": ["templates/*.html",
     "templates/admin/nudge/*.html",
      "templates/admin/nudge/batch/*.html",
      "templates/admin/nudge/setting/*.html"]},
      package_dir={"": "src"},
      install_requires=['django', 'django-reversion', 'pycrypto',],
      cmdclass = cmdclass,
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: Public Domain",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django",])
