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
      version="0.5",
      description="Use Nudge to (gently) push content between Django servers",
      author="Joshua Ruihley, Ross Karchner",
      author_email="dave@etianen.com",
      url="https://github.com/downloads/jroo/django-nudge/django-nudge-0.5.tar.gz",
      download_url="http://github.com/downloads/etianen/django-reversion/django-reversion-1.5.1.tar.gz",
      zip_safe=False,
      packages=["nudge", "nudge.demo"],
      package_dir={"": "src"},
      cmdclass = cmdclass,
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: Public Domain",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django",])
