const types = {
  ERROR: 'error',
  SUCCESS: 'success',
};

class Notification {
  constructor(message) {
    this.dispatch = 'notifications/notify';
    this.message = message;
  }
}

export class ErrorNotification extends Notification {
  constructor(message) {
    super(message);
    this.type = types.ERROR;
  }
}

export class SuccessNotification extends Notification {
  constructor(message) {
    super(message);
    this.type = types.SUCCESS;
  }
}
