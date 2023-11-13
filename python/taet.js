// ChatGPTからの応答を音声に変換して再生する関数
async function playVoicevoxAudio(text) {
  // VoicevoxのWeb APIエンドポイント
  const voicevoxApiEndpoint = 'ここにVoicevoxのWeb APIのエンドポイントを入力します';

  // リクエストのヘッダー情報を設定します（APIキーなど）
  const headers = {
    'Content-Type': 'application/json',
    // 他の必要なヘッダーパラメータを追加します
  };

  // リクエストのボディ情報を設定します
  const body = JSON.stringify({
    text: text,
    // 他の必要なパラメータを追加します
  });

  try {
    // VoicevoxのWeb APIにリクエストを送信して音声データを取得します
    const response = await fetch(voicevoxApiEndpoint, {
      method: 'POST',
      headers: headers,
      body: body,
    });

    // レスポンスから音声データを取得します
    const audioData = await response.arrayBuffer();

    // 音声データを再生します（例として、Web Audio APIを使用）
    const audioContext = new AudioContext();
    const audioBuffer = await audioContext.decodeAudioData(audioData);
    const audioSource = audioContext.createBufferSource();
    audioSource.buffer = audioBuffer;
    audioSource.connect(audioContext.destination);
    audioSource.start(0);
  } catch (error) {
    console.error('音声の再生エラー:', error);
  }
}

// ボタンクリックなどのイベントハンドラを設定し、ユーザーの入力を取得してChatGPTからの応答を表示し、音声で再生します
document.getElementById('submitBtn').addEventListener('click', async () => {
  const userInput = document.getElementById('userInput').value;

  // ChatGPTから応答を取得
  const chatGPTResponse = await getChatGPTResponse(userInput);

  // ChatGPTからの応答を表示
  document.getElementById('output').innerText = chatGPTResponse;

  // ChatGPTの応答を音声に変換して再生
  await playVoicevoxAudio(chatGPTResponse);
});
