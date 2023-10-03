import polling
import os
from selenium.common.exceptions import StaleElementReferenceException
import yaml
import logging
from selenium.webdriver.common.by import By

def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

def filter_elements_without_children(driver, path, parent, filters):
    # JavaScript code as a multiline string
    js_code = """
    function allTrue(e, trueFilters) {
        return trueFilters.every(n => e.outerHTML.includes(n));
    }

    function allFalse(e, filters) {
        return filters.every(n => !e.outerHTML.includes(n.substring(1)));
    }

    function getElementsByXPath(path, parent) {
        let results = [];
        let query = document.evaluate(path, parent || document.body,
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    const query = (path, parent, filterArray) => {
        const containsArray = filterArray.filter(n => n.charAt(0) != "!");
        const containsNOTArray = filterArray.filter(n => n.charAt(0) == "!");

        if (!path) {
            path = parent ? ".//*" : "//*";
        }

        const elements = getElementsByXPath(path, parent);
        return elements.filter(el => {
            return allTrue(el, containsArray) && allFalse(el, containsNOTArray);
        });
    };

    return query(arguments[0], arguments[1], arguments[2]);
    """
    
    elements = driver.execute_script(js_code, path, parent, filters)
    return elements

def filter_elements(driver, path, parent, children, filters):
    # JavaScript code as a multiline string
    js_code = """
    function allTrue(e, trueFilters) {
        return trueFilters.every(n => e.outerHTML.includes(n));
    }

    function allFalse(e, filters) {
        return filters.every(n => !e.outerHTML.includes(n.substring(1)));
    }

    function getElementsByXPath(path, parent) {
        let results = [];
        let query = document.evaluate(path, parent || document.body,
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    const query = (path, parent, children, filterArray) => {
        const containsArray = filterArray.filter(n => n.charAt(0) != "!");
        const containsNOTArray = filterArray.filter(n => n.charAt(0) == "!");

        if (!path) {
            path = parent ? ".//*" : "//*";
        }

        const elements = getElementsByXPath(path, parent);
        return elements.filter(el => {
            return el.children.length == children && allTrue(el, containsArray) && allFalse(el, containsNOTArray);
        });
    };

    return query(arguments[0], arguments[1], arguments[2], arguments[3]);
    """
    
    elements = driver.execute_script(js_code, path, parent, children, filters)
    return elements


def filter_path(driver, path, parent, children, filters):
# JavaScript code as a multiline string
    js_code = """

    function allTrue(e, trueFilters) {
        return trueFilters.every(n => e.outerHTML.includes(n));
    }

    function allFalse(e, filters) {
        return filters.every(n => !e.outerHTML.includes(n.substring(1)));
    }

    function getElementsByXPath(path, parent) {
        let results = [];
        let query = document.evaluate(path, parent || document.body,
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            results.push(query.snapshotItem(i));
        }
        return results;
    }

    const query = (path, parent, children, filterArray) => {
        const containsArray = filterArray.filter(n => n.charAt(0) != "!");
        const containsNOTArray = filterArray.filter(n => n.charAt(0) == "!");

        if (!path) {
            path = parent ? ".//*" : "//*";
        }

        const elements = getElementsByXPath(path, parent);
        return elements.find(el => {
            if (el.children.length == children) {
                return allTrue(el, containsArray) && allFalse(el, containsNOTArray);
            }
        });
    };

    return query(arguments[0], arguments[1], arguments[2], arguments[3]);
    """
    
    element = driver.execute_script(js_code, path, parent, children, filters)
    return element


# def filter_path(driver, path, parent, children, filters):
#     element = driver.execute_script("let allFalse = (e, filters) => {\
#     let falseArray = [];\
#     filters.forEach((n) => {\
#         if (!e.outerHTML.includes(n.substring(1))) {\
#             falseArray.push(\"false\");\
#         }\
#     });\
#     if (falseArray.length == filters.length) {\
#         return true;\
#     }\
#     else { return false;\
#     }\
# };\
# let allTrue = (e, trueFilters) => {\
#     let trueArray = [];\
#     trueFilters.forEach((n) => {\
#         if (e.outerHTML.includes(n)) {\
#             trueArray.push(\"true\");\
#         }\
#     });\
#     if (trueArray.length == trueFilters.length) {\
#         return true;\
#     } else { \
#         return false;\
#     }\
# };\
# const query = (path, parent, children, filterArray) => {\
#         const containsArray = filterArray.filter((n) => {\
#             if (n.charAt(0) != \"!\")\
#                 return n;\
#         });\
#         const containsNOTArray = filterArray.filter((n) => {\
#             if (n.charAt(0) == \"!\") {\
#                 return n;\
#             }\
#         });\
#             function getElementsByXPath(path, parent) {\
#                 let results = [];\
#                 let query = document.evaluate(path, parent || document.body,\
#                     null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);\
#                 for (let i = 0, length = query.snapshotLength; i < length; ++i) {\
#                     results.push(query.snapshotItem(i));\
#                 }\
#                 return results; \
#             };\
#             if (path != null) {\
#                 const elements = getElementsByXPath(path, parent);\
#                 const elem = elements.find(el => {\
#                     if (el.children.length == children) {\
#                         if (allTrue(el, containsArray) && allFalse(el, containsNOTArray)) {\
#                             return el;\
#                         }\
#                     }\
#                 });\
#                 return elem;\
#             } else {\
#                 if (parent != null) { \
#                     path = \".//*\";\
#                     } else { \
#                         path = \"//*\"; \
#                         };\
#                 const elements = getElementsByXPath(path, parent);\
#                 const elem = elements.find(el => {\
#                     if (el.children.length == children && el.outerHTML == webElement.outerHTML) {\
#                         if (allTrue(el, containsArray) && allFalse(el, containsNOTArray)) {\
#                             return el;\
#                         }\
#                     };\
#                 });\
#                 return elem;\
#             }\
# };\
# const element = await query(arguments[0], arguments[1], arguments[2], arguments[3]);\
# return element;", path, parent, children, filters);

#     return element

def get_element(driver, path, parent, children, filters):
    try:
        element = polling.poll(
        lambda: filter_path(driver, path, parent, children, filters),
        step=0.5,
        timeout=10)
        return element
    except:
        element = None
        return element

def scrollIntoView(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

def click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def getText(driver, element):
    driver.execute_script("return arguments[0].innerHTML;", element)

def selectTerminal(driver, text):
    driver.execute_script("function selectTerminal(text) { \
    let elements = document.querySelector('select[name=\"terminal\"]').getElementsByTagName('option'); \
    let eleArray = Object.values(elements);\
    let array = eleArray.filter((item) => {\
        if (item.innerHTML.includes(text)) {\
            return item;\
        };\
    });\
    let element = array[0]; \
    element.click();\
    };\
    selectTerminal(arguments[0]);", text)

def getRouteSelect(driver):
    select = driver.execute_script("function getRouteSelect() { \
    function getElementsByXPath(path, parent) {\
        let results = [];\
        let query = document.evaluate(\"//select\", document.body,\
            null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);\
        for (let i = 0, length = query.snapshotLength; i < \length; ++i) {\
            results.push(query.snapshotItem(i));\
        };\
        return results; \
    };\
    let elements = getElementsByXPath(path, parent);\
    let select = elements[4];\
    return select;\
    };\
    let select = getRouteSelect();\
    return select();")
    return select
    
def getRelativePath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    dir = '{}'.format(dirname)
    filename = os.path.join(dir, 'test-reports')
    relPath = filename.replace("\\", "/") + '/' 
    return relPath

def getConfig(arg):
    config = {}
    if arg == "Prod":
        with open('config.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    else:
        with open('config-dev.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def awaitAbsence(driver, path, parent, children, filters):
    try:
        try:
            element = polling.poll(
            lambda: filterPath(driver, path, parent, children, filters),
            step=0.5,
            timeout=60)
            if element == None:
                print("element null")
                return True
        except StaleElementReferenceException:
            print("stale element")
            return True
    except:
        return False

        
def gather_links(driver, url):
    driver.get(url)
    # Find all <a> tags on the page
    a_elements = driver.find_elements(By.TAG_NAME, 'a')
    # Extract href attributes from <a> tags and return them
    return [a.get_attribute('href') for a in a_elements if a.get_attribute('href')]

def get_links(driver, start_url):
    # Create a new Chrome session (make sure you've installed ChromeDriver
    # Lists to keep track of visited URLs and URLs to visit
    visited_urls = []
    urls_to_visit = [start_url]
    all_links = []

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)  # Get the first URL from the list

        if current_url not in visited_urls:
            print(f"Visiting: {current_url}")
            visited_urls.append(current_url)  # Mark the URL as visited
            
            # Gather links from the current URL
            links = gather_links(driver, current_url)
            all_links.extend(links)

            # Add newly found links to urls_to_visit, if they haven't been visited or added already
            for link in links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
    
    # Print and return all unique links
    all_unique_links = list(set(all_links))
    print(all_unique_links)
    return all_unique_links
