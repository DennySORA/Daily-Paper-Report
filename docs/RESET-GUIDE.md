# Daily Paper Report 網站重置指南

本文件記錄如何完全清除 Daily Paper Report 網站的所有資料。

## 為什麼重置這麼困難？

網站資料來自**三個獨立來源**，必須全部處理才能完全清除：

```
┌─────────────────────────────────────────────────────────────┐
│                      資料來源架構                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. State Branch (GitHub)                                   │
│     └── state.sqlite + archives/                            │
│         ↓                                                   │
│  2. GitHub Pages (Live Site)                                │
│     └── 已部署的 archives/*.json                            │
│         ↓ (工作流程會從這裡還原！)                           │
│  3. Fresh Collection                                        │
│     └── arXiv API 即時抓取                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 關鍵問題

工作流程中有一個步驟會**從已部署的網站下載舊資料**：

```yaml
# .github/workflows/daily-digest.yaml 第 167-186 行
- name: Restore archive pages from GitHub Pages
  run: |
    # 從 https://paper.sorahane-kyoukai.org/api/archives/ 下載所有 JSON
```

這代表即使你刪除了 state branch，工作流程執行時仍會從線上網站還原資料！

## 完整重置步驟

### 前置條件

- 已安裝 GitHub CLI (`gh`)
- 已登入：`gh auth login`

### 步驟 1：取消正在執行的工作流程

```bash
# 查看正在執行的工作流程
gh run list --repo DennySORA/Daily-Paper-Report --status in_progress

# 取消所有執行中的工作流程
for ID in $(gh run list --repo DennySORA/Daily-Paper-Report --status in_progress --status queued --json databaseId --jq '.[].databaseId'); do
  gh run cancel "$ID" --repo DennySORA/Daily-Paper-Report
done
```

### 步驟 2：刪除 State Branch

```bash
# 確認 state branch 存在
gh api repos/DennySORA/Daily-Paper-Report/branches/state

# 刪除 state branch
gh api -X DELETE repos/DennySORA/Daily-Paper-Report/git/refs/heads/state
```

### 步驟 3：觸發乾淨的部署

**這是最關鍵的步驟！** 必須使用特殊參數來跳過資料還原：

```bash
gh workflow run daily-digest.yaml \
  --repo DennySORA/Daily-Paper-Report \
  --ref main \
  -f reset_state=true \
  -f skip_archive_restore=true \
  -f backfill_days=0 \
  -f lookback_hours=1
```

參數說明：
| 參數 | 值 | 說明 |
|------|-----|------|
| `reset_state` | `true` | 不使用舊的 state.sqlite |
| `skip_archive_restore` | `true` | **不從線上網站還原舊資料** |
| `backfill_days` | `0` | 不回填歷史資料 |
| `lookback_hours` | `1` | 最小化資料抓取（加快速度） |

### 步驟 4：監控工作流程

```bash
# 取得最新的工作流程 ID
RUN_ID=$(gh run list --repo DennySORA/Daily-Paper-Report --limit 1 --json databaseId --jq '.[0].databaseId')

# 監控執行狀態
gh run watch $RUN_ID --repo DennySORA/Daily-Paper-Report

# 或查看詳細狀態
gh run view $RUN_ID --repo DennySORA/Daily-Paper-Report
```

### 步驟 5：驗證重置成功

```bash
# 檢查網站 API
curl -s https://paper.sorahane-kyoukai.org/api/daily.json | jq '{
  papers_count: (.papers | length),
  archive_dates: .archive_dates
}'
```

預期輸出（重置成功）：
```json
{
  "papers_count": 0,
  "archive_dates": ["2026-02-23"]
}
```

## 方法一：使用 GitHub Actions（推薦）

最簡單的方法是使用獨立的 Reset Site workflow：

### 透過 GitHub Web UI

1. 前往 [Actions 頁面](https://github.com/DennySORA/Daily-Paper-Report/actions/workflows/reset-site.yaml)
2. 點擊 "Run workflow"
3. 在 `confirm_reset` 欄位輸入 `RESET`
4. 點擊 "Run workflow" 按鈕

### 透過命令列

```bash
gh workflow run reset-site.yaml \
  --repo DennySORA/Daily-Paper-Report \
  -f confirm_reset=RESET
```

這個 workflow 會自動：
1. 驗證確認輸入
2. 刪除 state branch
3. 部署空白網站

## 方法二：使用本地腳本

如果你想在本地執行：

```bash
# 互動模式（會要求確認）
./scripts/reset-site.sh

# 自動確認模式
./scripts/reset-site.sh --confirm

# 預覽模式（顯示會執行什麼但不實際執行）
./scripts/reset-site.sh --dry-run
```

## 重置後回填資料

當你準備好重新收集資料時：

```bash
# 回填 7 天資料
gh workflow run daily-digest.yaml \
  --repo DennySORA/Daily-Paper-Report \
  --ref main \
  -f backfill_days=7 \
  -f lookback_hours=168
```

## 常見問題

### Q: 我刪除了 state branch 但資料還在？

這是因為工作流程會從已部署的網站還原資料。必須使用 `skip_archive_restore=true` 參數。

### Q: Persist State to Branch 步驟失敗？

如果你剛刪除了 state branch，這個步驟會失敗，這是**預期行為**，不影響網站重置。下次執行時會自動建立新的 state branch。

### Q: 工作流程執行很久？

使用 `lookback_hours=1` 可以大幅縮短時間，因為只會抓取最近 1 小時的論文（通常為 0 篇）。

### Q: 如何只清除特定日期的資料？

目前不支援部分清除。如需此功能，需要修改工作流程。

## 技術細節

### 相關檔案

- `.github/workflows/daily-digest.yaml` - 工作流程定義
  - 第 158 行：跳過還原的條件判斷
  - 第 167-186 行：從 GitHub Pages 還原 archives 的步驟
- `scripts/reset-site.sh` - 自動化重置腳本
- `src/cli/digest.py` - Digest pipeline 主程式

### 工作流程參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `lookback_hours` | `36` | 向前搜尋幾小時的論文 |
| `backfill_days` | `0` | 回填幾天的歷史資料 |
| `reset_state` | `false` | 是否重置 state.sqlite |
| `skip_archive_restore` | `false` | 是否跳過從線上還原 archives |

---

*最後更新：2026-02-23*
