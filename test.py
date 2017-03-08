from bs4 import BeautifulSoup

html_str = '<td class="first">innoscripta GmbH<br/>M\xfcnchen\n                                    </td>'
name = BeautifulSoup(html_str, "lxml")
print name.text