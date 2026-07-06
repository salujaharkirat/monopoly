// frontend/src/services/animation.js
export class AnimationService {
  constructor() {
    this.animations = {};
  }

  animatePlayerMovement(playerId, fromPosition, toPosition, onStep) {
    const steps = this.calculatePath(fromPosition, toPosition);
    let currentStep = 0;
    
    // Clear any existing animation for this player
    if (this.animations[playerId]) {
      clearInterval(this.animations[playerId]);
    }
    
    // Animate step by step
    this.animations[playerId] = setInterval(() => {
      if (currentStep < steps.length) {
        const position = steps[currentStep];
        onStep(playerId, position);
        currentStep++;
      } else {
        clearInterval(this.animations[playerId]);
        delete this.animations[playerId];
      }
    }, 300); // 300ms per step
  }

  calculatePath(from, to) {
    const path = [];
    let current = from;
    
    while (current !== to) {
      current = (current + 1) % 40;
      path.push(current);
    }
    
    return path;
  }

  stopAnimation(playerId) {
    if (this.animations[playerId]) {
      clearInterval(this.animations[playerId]);
      delete this.animations[playerId];
    }
  }

  stopAllAnimations() {
    Object.keys(this.animations).forEach(playerId => {
      clearInterval(this.animations[playerId]);
      delete this.animations[playerId];
    });
  }
}

export default new AnimationService();