import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        scan: resolve(__dirname, 'scan.html'),
        result: resolve(__dirname, 'result.html'),
        privacy: resolve(__dirname, 'privacy.html'),
        terms: resolve(__dirname, 'terms.html'),
        about: resolve(__dirname, 'about.html'),
        'name-youngsoo': resolve(__dirname, 'name/youngsoo.html'),
        'name-youngho': resolve(__dirname, 'name/youngho.html'),
        'name-youngsik': resolve(__dirname, 'name/youngsik.html'),
        'name-youngchul': resolve(__dirname, 'name/youngchul.html'),
        'name-kwangsoo': resolve(__dirname, 'name/kwangsoo.html'),
        'name-sangchul': resolve(__dirname, 'name/sangchul.html'),
        'name-oksoon': resolve(__dirname, 'name/oksoon.html'),
        'name-youngsook': resolve(__dirname, 'name/youngsook.html'),
        'name-soonja': resolve(__dirname, 'name/soonja.html'),
        'name-youngja': resolve(__dirname, 'name/youngja.html'),
        'name-jungsook': resolve(__dirname, 'name/jungsook.html'),
        'name-hyunsook': resolve(__dirname, 'name/hyunsook.html')
      }
    }
  }
});
