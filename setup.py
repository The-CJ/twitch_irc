import setuptools, re

with open("README.md", "r") as rm:
	long_description = rm.read()

try:
	version = re.findall(r"^__version__\s?=\s?[\'\"](.+)[\'\"]$", open("twitch_irc/__init__.py").read(), re.M)[0]
except IndexError:
	raise RuntimeError('Unable to determine version.')

setuptools.setup(
	name="twitch_irc",
	version=version,
	author="The_CJ",
	author_email="dev@phaaze.net",
	description="IRC connection for Twitch",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/The-CJ/twitch_irc",
	packages=["twitch_irc"],
	classifiers=[
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
)
