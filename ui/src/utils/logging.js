import axios from 'axios';

const ENABLE_LOGGING = false;
const LOG_TO_GA = false;

export async function logEvent(gtag, sourcePath, path, action, category, label) {
  if (!ENABLE_LOGGING) return;

  // DEBUG
//  console.log("log event sourcePath=" + sourcePath + " path=" + path + " action=" + action + " category=" + category + " abel=" + label);
    
  if (LOG_TO_GA && (gtag != null)) gtag.event(action, {'event_category': category, 'event_label': label});
    
  axios
    .post(`/api/log`, {
      sourcePath: sourcePath,
      path: path,
      action: action,
      category: category,
      label: label,
    })
    .then(response => {
      //	console.log("/api/log returned status = " + response.status);
    })
    .catch(error => {
      console.log('/api/log failed with status ' + error.response.status);
    });
}
