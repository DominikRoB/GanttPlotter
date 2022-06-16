from setuptools import setup

setup(
    name="GanttPlotter",
    packages=["GanttPlotter"],
    version="0.0.3",
    install_requires=[
        "matplotlib==3.5.1",
    ],
    keywords=["Gantt", "Chart", "Plotting", "Supply chain management", "Scheduling"],
    description="A set of functions to create gantts quickly using Matplotlib",
    author="Dominik Bleidorn",
    author_email="dominik.bleidorn@inosim.com",
    # url='https://github.com/user/reponame',
    classifiers=[
        "Development Status :: 3 - Alpha",
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Programming Language :: Python :: 3",  # Specify which python versions that you want to support
        "Programming Language :: Python :: 3.9",
    ],
)
