import { test, expect } from '@playwright/test'

test.describe('Calendar and booking flow', () => {
  test('shows calendar page and counselor filter', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: /谈话预约/ })).toBeVisible()
    await expect(page.getByLabel(/选择辅导员/)).toBeVisible()
  })

  test('calendar loads availability automatically', async ({ page }) => {
    await page.goto('/')
    // Navigation controls should appear immediately
    await expect(page.getByRole('button', { name: '上一周' })).toBeVisible()
    await expect(page.getByRole('button', { name: '下一周' })).toBeVisible()
    // Availability data loads automatically from the backend
    await expect(page.getByRole('button', { name: '可约' }).first()).toBeVisible({ timeout: 10000 })
  })

  test('navigate to book form and submit', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('button', { name: '可约' }).first()).toBeVisible({ timeout: 10000 })
    await page.getByRole('button', { name: '可约' }).first().click()
    await expect(page).toHaveURL(/\/book/)
    await expect(page.getByRole('heading', { name: /填写预约/ })).toBeVisible()
    await page.getByLabel(/谈话内容/).fill('E2E 测试预约')
    await page.getByLabel(/联系人姓名/).fill('测试用户')
    await page.getByLabel(/联系电话/).fill('13800138000')
    await page.getByRole('button', { name: /提交预约/ }).click()
    await expect(page).toHaveURL(/\/success/, { timeout: 10000 })
    await expect(page.getByText(/预约成功/)).toBeVisible()
  })
})
