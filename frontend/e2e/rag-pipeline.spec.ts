import { test, expect } from '@playwright/test';

test.describe('RAG Pipeline E2E Test', () => {
  test.beforeAll(async () => {
    await fetch('http://localhost:8000/api/llm/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: 'gemini' })
    });
  });

  test('backend health check', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    expect(response.ok()).toBe(true);

    const data = await response.json();
    expect(data).toHaveProperty('status');
  });

  test('upload document via API', async () => {
    const fileContent = `
# RAG Test Document

## What is RAG?
RAG stands for Retrieval-Augmented Generation. It is a technique that combines the strengths of large language models with information retrieval systems.

## How RAG Works
1. Document Processing: Documents are uploaded, parsed, and split into chunks.
2. Embedding Generation: Each chunk is converted into a vector embedding.
3. Vector Storage: These embeddings are stored in a vector database.
4. Query Processing: When a user asks a question, the system retrieves relevant document chunks.
5. Response Generation: The LLM generates a response based on the retrieved context.
    `.trim();

    const buffer = Buffer.from(fileContent);
    const formData = new FormData();
    formData.append('file', new Blob([buffer], { type: 'text/plain' }), 'test_document.txt');

    const response = await fetch('http://localhost:8000/api/documents/upload', {
      method: 'POST',
      body: formData
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty('document_id');
    expect(data).toHaveProperty('status', 'processed');
    expect(data).toHaveProperty('filename', 'test_document.txt');
  });

  test('list documents via API', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/documents');
    expect(response.ok()).toBe(true);

    const documents = await response.json();
    expect(Array.isArray(documents)).toBe(true);
  });

  test('chat with documents via API', async () => {
    const documentsResponse = await fetch('http://localhost:8000/api/documents');
    const documents = await documentsResponse.json();
    expect(documents.length).toBeGreaterThan(0);

    const firstDocumentId = documents[0].id;

    const chatResponse = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'What is RAG?',
        document_ids: [firstDocumentId]
      })
    });

    expect(chatResponse.ok).toBe(true);
    const chatData = await chatResponse.json();
    expect(chatData).toHaveProperty('response');
    expect(chatData).toHaveProperty('conversation_id');
    expect(chatData).toHaveProperty('message_id');
    expect(chatData.response.toLowerCase()).toContain('rag');
  });

  test('frontend page loads', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('h1')).toContainText('RAG Document Assistant');
  });

  test('LLM provider selector visible', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('[data-testid="llm-provider-selector"]')).toBeVisible();
  });

  test('document list renders', async ({ page }) => {
    await page.goto('/');

    await page.waitForTimeout(2000);

    await expect(page.locator('[data-testid="document-list"]')).toBeVisible();
  });

  test('upload document via UI', async ({ page }) => {
    await page.goto('/');

    const fileContent = 'Test document for upload';
    const fileInput = page.locator('input[type="file"]');

    await fileInput.setInputFiles({
      name: 'ui_test_document.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(fileContent)
    });

    await expect(page.locator('text=/uploaded successfully/i')).toBeVisible({ timeout: 30000 });
  });

  test('complete RAG pipeline via UI', async ({ page }) => {
    await page.goto('/');

    const fileContent = `
# UI Test Document

## Test Content
This is a test document for the RAG pipeline.
RAG stands for Retrieval-Augmented Generation.
It combines LLMs with information retrieval.
    `.trim();

    await page.locator('input[type="file"]').setInputFiles({
      name: 'rag_pipeline_test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(fileContent)
    });

    await expect(page.locator('text=/uploaded successfully/i')).toBeVisible({ timeout: 30000 });

    await page.waitForTimeout(5000);

    await page.reload();

    await page.waitForTimeout(2000);

    const documentList = page.locator('[data-testid="document-list"]');
    await expect(documentList).toBeVisible();

    const documents = await documentList.locator('div').all();
    expect(documents.length).toBeGreaterThan(0);

    const firstDoc = documentList.locator('div').filter({ hasText: /rag_pipeline_test.txt/ }).first();
    if (await firstDoc.count() > 0) {
      await firstDoc.click();
      await page.waitForTimeout(2000);

      const chatInput = page.locator('textarea');
      await chatInput.fill('What is RAG?');

      const sendButton = page.locator('button[type="submit"]');
      await sendButton.click();

      await expect(page.locator('.chat-message.assistant')).toBeVisible({ timeout: 60000 });

      const response = page.locator('.chat-message.assistant').last();
      await expect(response).toBeVisible();
      const responseText = await response.textContent();
      expect(responseText?.toLowerCase()).toContain('rag');
    }
  });
});
