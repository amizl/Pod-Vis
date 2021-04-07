import axios from 'axios';

const ENABLE_LOGGING = true;
const LOG_TO_GA = false;

async function logEvent(gtag, sourcePath, path, action, category, label) {
  if (!ENABLE_LOGGING) return;

  // DEBUG
  //  console.log("log event sourcePath=" + sourcePath + " path=" + path + " action=" + action + " category=" + category + " label=" + label);

  if (LOG_TO_GA && gtag != null)
    gtag.event(action, { event_category: category, event_label: label });

  axios
    .post(`/api/log`, {
      sourcePath: sourcePath,
      path: path,
      action: action,
      category: category,
      label: label,
    })
    .then(() => {
      //	console.log("/api/log returned status = " + response.status);
    })
    .catch(() => {
      //      console.log('/api/log failed with status ' + error.response.status);
    });
}

export default logEvent;
