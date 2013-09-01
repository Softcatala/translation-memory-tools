#!/bin/bash
# Creates a zip file to distribute the translation memory

zip -r "tm-sc-$(date +"%Y-%m-%d").zip" po/*.po tmx/*.tmx *.txt
