import type { NodeExplanation } from '@/types';

export const DEMO_EXPLANATIONS: Record<string, NodeExplanation> = {
  'n-root': {
    id: 'exp-root',
    node_id: 'n-root',
    overview:
      'Machine Learning is a subfield of artificial intelligence dedicated to developing algorithms that discover patterns in empirical data to make predictions or decisions without explicit procedural programming.',
    detailed_explanation:
      'At its core, machine learning reformulates problems from deterministic software development into mathematical optimization. Rather than hand-crafting edge cases, developers design loss functions and neural or statistical architectures. The model iteratively adjusts internal parameters (weights and biases) via gradient descent until its predictions align with the underlying data distribution.',
    how_it_works: [
      'Data Ingestion & Preprocessing: Raw observations are cleaned, tokenized or normalized into multi-dimensional numerical tensors.',
      'Model Architecture Initialization: Mathematical functions (decision trees, linear layers, attention heads) are instantiated with random or pretrained weights.',
      'Forward Propagation: Input batches pass through the model to produce output hypotheses.',
      'Loss Computation: An objective function (Mean Squared Error, Cross-Entropy) measures discrepancy against target truth.',
      'Backpropagation & Optimization: Gradients are computed with respect to parameters, and optimizers (Adam, SGD) update weights to minimize loss.',
    ],
    examples: [
      'Image Recognition: Convolutional neural networks detecting anomalies in medical MRI scans.',
      'Natural Language Processing: Large language models translating multi-lingual documents and summarizing legal contracts.',
      'Recommendation Systems: Collaborative filtering algorithms personalizing video feeds for millions of concurrent users.',
    ],
    applications: [
      'Autonomous Vehicles: Real-time sensor fusion and path planning in dynamic traffic environments.',
      'Financial Fraud Detection: Flagging irregular transaction velocities in sub-100ms banking pipelines.',
      'Genomics & Drug Discovery: Predicting 3D protein folding configurations to design novel therapeutics.',
    ],
    key_concepts: [
      'Generalization',
      'Loss Function',
      'Overfitting',
      'Gradient Descent',
      'Hyperparameters',
    ],
    related_concepts: [
      'Supervised Learning',
      'Unsupervised Learning',
      'Reinforcement Learning',
      'Neural Networks',
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  'n-sup': {
    id: 'exp-sup',
    node_id: 'n-sup',
    overview:
      'Supervised Learning is the machine learning paradigm where an algorithm trains on pairs of input features and ground-truth output labels to learn a predictive mapping function.',
    detailed_explanation:
      'In supervised learning, the training dataset acts as a supervisor or teacher. The algorithm makes predictions on input data and is corrected whenever its outputs diverge from the expected labels. Supervised learning splits fundamentally into Classification (predicting categorical labels) and Regression (predicting continuous numerical quantities).',
    how_it_works: [
      'Label Ingestion: Features X and verified target labels Y are organized into parallel tensors.',
      'Mapping Function: Model f(X) parameterized by θ generates prediction Y_hat.',
      'Error Minimization: The loss L(Y, Y_hat) penalizes incorrect predictions.',
      'Validation Testing: Model performance is evaluated on unseen holdout test sets to prevent memorization/overfitting.',
    ],
    examples: [
      'Spam Filtering: Classifying incoming emails as "Spam" or "Inbox" based on text features.',
      'Real Estate Valuation: Predicting property prices based on square footage, zip code, and bedroom count.',
      'Credit Risk Modeling: Predicting default probabilities on commercial loan applications.',
    ],
    applications: [
      'Medical Diagnostic Screening: Classifying biopsy tissue samples as benign or malignant.',
      'Speech Recognition: Converting acoustic audio waveforms into written phonetic transcripts.',
      'Predictive Maintenance: Forecasting machinery equipment failure hours in manufacturing plants.',
    ],
    key_concepts: [
      'Labeled Dataset',
      'Ground Truth',
      'Classification',
      'Regression',
      'Bias-Variance Tradeoff',
    ],
    related_concepts: ['Classification', 'Regression', 'Machine Learning'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  'n-unsup': {
    id: 'exp-unsup',
    node_id: 'n-unsup',
    overview:
      'Unsupervised Learning entails discovering inherent structures, cluster groupings, and latent probability distributions within unlabeled datasets without human supervision.',
    detailed_explanation:
      'Because the vast majority of real-world data is unlabeled, unsupervised learning is crucial for self-supervised representation learning. Algorithms analyze internal statistical similarities to group data (Clustering) or compress redundant dimensions into informative low-dimensional representations (Dimensionality Reduction).',
    how_it_works: [
      'Distance Metric Definition: Euclidean, Manhattan, or Cosine similarity measures proximity between data points.',
      'Centroid Optimization: In K-Means, cluster centers are iteratively updated to minimize intra-cluster variance.',
      'Eigenvector Decomposition: In PCA, high-variance axes are identified to compress feature spaces.',
    ],
    examples: [
      'Customer Segmentation: Partitioning e-commerce users into behavioral cohorts based on shopping frequency.',
      'Dimensionality Reduction: Compressing 10,000 genomic features into 2D plots using t-SNE or UMAP.',
      'Anomaly Detection: Identifying outlier server access requests that diverge from typical baseline traffic.',
    ],
    applications: [
      'Market Basket Analysis: Discovering co-purchased grocery items to optimize retail shelf layouts.',
      'Cybersecurity: Detecting novel zero-day network intrusions that deviate from normal usage profiles.',
      'Astronomy: Categorizing distant galactic spectra into celestial clusters without prior templates.',
    ],
    key_concepts: [
      'Clustering',
      'Dimensionality Reduction',
      'Latent Representations',
      'K-Means',
      'PCA',
    ],
    related_concepts: ['Clustering', 'Machine Learning', 'Supervised Learning'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  'n-rl': {
    id: 'exp-rl',
    node_id: 'n-rl',
    overview:
      'Reinforcement Learning is an agent-centric paradigm where an autonomous policy learns sequential decision-making through trial-and-error feedback guided by scalar reward signals.',
    detailed_explanation:
      'Formalized as a Markov Decision Process (MDP), an agent observes an environment state S_t, selects an action A_t according to its policy π, transitions to a new state S_{t+1}, and receives a reward R_t. The objective is to maximize the expected cumulative discounted future reward rather than immediate short-term payoff.',
    how_it_works: [
      'Environment Loop: Agent samples actions and observes transitions from environment simulators.',
      'Credit Assignment: Calculating which specific action in a long sequence caused eventual victory or defeat.',
      'Exploration vs. Exploitation: Balancing trying unknown actions against executing known high-reward strategies.',
      'Policy Optimization: Updating policy parameters or action-value Q-tables via Bellman optimality equations.',
    ],
    examples: [
      'Game Playing: DeepMind AlphaGo and AlphaZero mastering complex board games against human world champions.',
      'Robotics Control: Quadruped robots learning stable balance and locomotion across irregular rough terrain.',
      'HVAC Optimization: Deep RL managing cooling systems in global data centers to reduce power consumption by 40%.',
    ],
    applications: [
      'Algorithmic High-Frequency Trading: Executing optimal limit order book placements.',
      'Autonomous Drone Flight: Maneuvering agile quadcopters through dense forest obstacles.',
      'Traffic Light Synchronization: Optimizing city grid signal intervals to minimize commuter congestion.',
    ],
    key_concepts: [
      'Agent & Environment',
      'Reward Function',
      'Markov Decision Process',
      'Policy Gradient',
      'Q-Learning',
    ],
    related_concepts: ['Q-Learning & Policy Search', 'Actor-Critic Models', 'Machine Learning'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
};
