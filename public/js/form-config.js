/*
 * フォーム送信の設定
 * ------------------------------------------------------------
 * お問い合わせ・応募フォームの内容は Web3Forms（無料）を通じて
 * メールで届きます。https://web3forms.com で受信用メールアドレスを
 * 入力すると「Access Key」がメールで届くので、下の "" の中に貼り付けてください。
 * （このキーは公開されても問題ない種類のものです）
 */
window.FORM_CONFIG = {
  accessKey: "",
  endpoint: "https://api.web3forms.com/submit",
  subjects: {
    contact: "【ホームページ】お問い合わせがありました",
    recruit: "【ホームページ】採用の応募がありました"
  }
};
