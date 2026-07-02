from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import math
import time


def click_element(driver, by_type, name):
	"""Find and click an element by 'id' or 'class'.

	Parameters:
	- driver: Selenium WebDriver
	- by_type: 'id' or 'class'
	- name: the id or class name string
	"""
	if by_type == 'id':
		element = driver.find_element(By.ID, name)
	elif by_type == 'class':
		element = driver.find_element(By.CLASS_NAME, name)
	else:
		raise ValueError("by_type must be 'id' or 'class'")

	driver.execute_script("arguments[0].scrollIntoView(true);", element)
	time.sleep(0.5)
	element.click()


def find_elements(driver, by_type, name):
	"""Find all elements by 'id', 'class', or 'css'."""
	if by_type == 'id':
		return driver.find_elements(By.ID, name)
	elif by_type == 'class':
		return driver.find_elements(By.CLASS_NAME, name)
	elif by_type == 'css':
		return driver.find_elements(By.CSS_SELECTOR, name)
	else:
		raise ValueError("by_type must be 'id', 'class', or 'css'")


def click_elements_by_css_indices(driver, css_selector, indices):
	"""Click matching elements by their DOM order indices."""
	elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
	for index in indices:
		if index >= len(elements):
			raise IndexError(f"Not enough elements for selector {css_selector!r}; needed index {index}, found {len(elements)}")
		element = elements[index]
		driver.execute_script("arguments[0].scrollIntoView(true);", element)
		time.sleep(0.5)
		element.click()


def get_level_3_answer(driver):
	"""Read the current wiggles captcha answer from the Vue app state."""
	return driver.execute_script(
		"""
		const findCaptchaComponent = (vm) => {
			if (!vm) return null;
			const data = vm.$data || {};
			if (Array.isArray(data.captchas) && typeof data.index === 'number') {
				return data.captchas[data.index];
			}
			for (const child of (vm.$children || [])) {
				const found = findCaptchaComponent(child);
				if (found) return found;
			}
			return null;
		};

		return findCaptchaComponent(window.$nuxt);
		"""
	)


def solve_level_4_vegetables(driver):
	"""Select the vegetable tiles, regardless of their randomized order."""
	target_names = {"carrot", "onion", "corn", "potato", "eggplant"}
	image_elements = driver.find_elements(By.CSS_SELECTOR, '.vegetable-image, .grid-item-with-image img')
	for image in image_elements:
		src = image.get_attribute('src') or ''
		file_name = src.rsplit('/', 1)[-1].split('.', 1)[0]
		if file_name in target_names:
			driver.execute_script("arguments[0].scrollIntoView(true);", image)
			time.sleep(0.2)
			image.click()


def get_rotation_degrees(driver, element):
	"""Return the current rotation angle for an element in degrees."""
	return driver.execute_script(
		r"""
		const element = arguments[0];
		const styles = window.getComputedStyle(element);
		const rotateValue = element.style.rotate || styles.rotate || '';
		const transformValue = element.style.transform || styles.transform || '';
		const parseAngle = (value) => {
			const match = String(value).match(/rotate\((-?\d+(?:\.\d+)?)deg\)/i);
			return match ? parseFloat(match[1]) : null;
		};
		const directAngle = parseAngle(rotateValue) ?? parseAngle(transformValue);
		if (directAngle !== null) {
			return directAngle;
		}
		if (transformValue && transformValue !== 'none') {
			const matrix = transformValue.match(/matrix\(([^)]+)\)/i);
			const matrix3d = transformValue.match(/matrix3d\(([^)]+)\)/i);
			const values = matrix ? matrix[1].split(',').map(Number) : matrix3d ? matrix3d[1].split(',').map(Number) : null;
			if (values) {
				const a = values[0];
				const b = values[1];
				return Math.round(Math.atan2(b, a) * (180 / Math.PI));
			}
		}
		return 0;
		""",
		element,
	)


def click_element_forcefully(driver, element):
	"""Click an element using Selenium actions with a JS fallback."""
	driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
	time.sleep(0.15)
	try:
		ActionChains(driver).move_to_element(element).click().perform()
	except Exception:
		try:
			element.click()
		except Exception:
			driver.execute_script("arguments[0].click();", element)


def click_rotating_items_until_multiple_of_360(driver, by_type, name):
	"""Click every matching rotating item at least once until its rotation is a multiple of 360 degrees."""
	for index in range(50):
		elements = find_elements(driver, by_type, name)
		if index >= len(elements):
			break

		clicks = 0
		attempts = 0
		while attempts < 30:
			elements = find_elements(driver, by_type, name)
			if index >= len(elements):
				break

			element = elements[index]
			click_element_forcefully(driver, element)
			clicks += 1
			time.sleep(0.2)

			current_angle = get_rotation_degrees(driver, element)
			if clicks >= 1 and math.isclose(current_angle % 360, 0.0, abs_tol=0.5):
				break
			attempts += 1


def wait_for_level_6_tic_tac_toe(driver, timeout_seconds=30):
	"""Wait until the level 6 Vue component has mounted."""
	deadline = time.time() + timeout_seconds
	while time.time() < deadline:
		found = driver.execute_script(
			"""
			const findComponent = (vm) => {
				if (!vm) return null;
				const methods = vm.$options && vm.$options.methods;
				if (methods && methods.checkVerify) {
					return vm;
				}
				for (const child of (vm.$children || [])) {
					const found = findComponent(child);
					if (found) return found;
				}
				return null;
			};

			return !!findComponent(window.$nuxt);
			"""
		)
		if found:
			return
		time.sleep(0.25)
	raise TimeoutError("Timed out waiting for the level 6 tic-tac-toe Vue component to mount.")


def solve_level_6_xoxo_vue(driver):
	"""Bypass the tic-tac-toe AI by setting the Vue game state to an X win."""
	wait_for_level_6_tic_tac_toe(driver)
	driver.execute_script(
		"""
		const findComponent = (vm) => {
			if (!vm) return null;
			const methods = vm.$options && vm.$options.methods;
			if (methods && methods.checkVerify) {
				return vm;
			}
			for (const child of (vm.$children || [])) {
				const found = findComponent(child);
				if (found) return found;
			}
			return null;
		};

		const wrapper = findComponent(window.$nuxt);
		if (!wrapper) {
			throw new Error('Unable to locate the level 6 Vue wrapper.');
		}

		const game = wrapper.$parent;
		if (!game) {
			throw new Error('Unable to locate the tic-tac-toe Vue instance.');
		}

		game.grid = ['X', 'X', 'X', null, 'O', null, null, null, null];
		game.winner = 'X';
		game.winningLine = [0, 1, 2];
		game.currentPlayer = 'O';
		game.lastSelected = 2;
		"""
	)

	time.sleep(0.2)
	click_element(driver, 'id', 'captcha-verify-button')


def main():
	options = Options()
	options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
	options.add_experimental_option('useAutomationExtension', False)
	options.add_experimental_option("detach", True)

	service = Service(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=options)
	driver.maximize_window()
	driver.get("https://neal.fun/not-a-robot/")

	# print message for opening the neal.fun website url
	print("Chrome opened and navigating to https://neal.fun/not-a-robot/. Press Ctrl+C to exit.")

	# =============================================================
	# LEVEL 1
	# =============================================================
	
	click_element(driver, 'class', 'recaptcha-container')

	time.sleep(5)


	# =============================================================
	# LEVEL 2
	# =============================================================

	click_elements_by_css_indices(
		driver,
		'.grid-item.grid-item-with-image',
		[2, 3, 6, 7],
	)

	click_element(driver, 'id', 'captcha-verify-button')

	

	time.sleep(5)


	# =============================================================
	# LEVEL 3
	# =============================================================

	level_3_answer = get_level_3_answer(driver)
	answer_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Answer"]')
	answer_input.clear()
	answer_input.send_keys(level_3_answer)

	time.sleep(0.2)

	click_element(driver, 'class', 'captcha-button')

	time.sleep(5)

	# =============================================================
	# LEVEL 4
	# =============================================================

	solve_level_4_vegetables(driver)
	click_element(driver, 'id', 'captcha-verify-button')

	time.sleep(5)


	# =============================================================
	# LEVEL 5
	# =============================================================

	click_rotating_items_until_multiple_of_360(driver, 'class', 'rotating-item')

	click_element(driver, 'id', 'captcha-verify-button')
	time.sleep(5)

	# =============================================================
	# LEVEL 6
	# =============================================================
	solve_level_6_xoxo_vue(driver)

	time.sleep(5)



	print("All levels completed. The browser will remain open for 1 hour.")

	time.sleep(5)


	while True:
		time.sleep(3600)


if __name__ == "__main__":
	main()