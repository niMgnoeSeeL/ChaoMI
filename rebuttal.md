# Rebuttal for the submission "Accounting for Missing Events in Statistical Information Leakage Testing"

We would like to thank the reviewers for their comments and feedback. We have addressed the comments and concerns raised by the reviewers in the following rebuttal. Below, we list the issues raised by the reviewers and provide our responses. Who commented the issues is presented in the parentheses.

## Comparison with the symbolic execution (SE)/model-counting (MC) based approach (R2, R3)

The reviewers raised concerns about not having a comparison with the model-counting based approach with the proposed approach. 
In this work, we focus on the purely statistical methodology for information leakage testing, and comparison with the SE/MC-based approach is out of the scope of this work.
We want to clarify that our claim does not argue that the statistical approach is always better than the SE/MC-based approach in all scalability issue. Some of the recent works have shown that the SE/MC-based approach is scalable and efficient for large-scale systems (Saha, 2023 and Bao, 2021) by itself or in combination with the statistical approach.
However, the SE/MC-based approach can be infeasible for some systems simply because it consists of operations that exist beyond the scope of the SE or MC tools. For instance,
```c
int val = call("./some_script.sh");
```
invoking a external script or a system call, reading a file, or getting a network packet, etc., in the code will make the SE/MC tools to lose the track of the system state. In such cases, while the SE/MC-based approach is infeasible, the language-agnotic statistical approach plays a unique role to handle the situation, which is the main focus of this work.
The core limitation of the statistical method is different from the SE/MC-based method; it is the sample size. The existing statistical methods are either producing inaccurate or unsafe result when the sample size is small. We address this limitation by proposing a new method employing the biostatistical approach to estimate the mutual information with a small sample size. We believe that our novel finding is valuable and contributes not only to the statistical method but also in general to the information leakage testing through hybridizing with the SE/MC-based approach.

## Representative Subject for the Realistic Security Domain (R2, R3)

The reviewers raised concerns about the representative of the subjects used in the experiments. They suggested that the subjects should be more representative of the realistic security domain. We agree with the reviewers' comments and have performed additional experiments to show the usefulness of our approach in a realistic security domain.
Especially, we performed experiments on the stream cipher, similar to the one presented in the LeakWatch paper. The experiment uses the estimated mutual information (MI) between the bit-flip event (secret) and the output of the cipher system (observable) for each bit of the internal state to analyze 1) which bits of its internal state are leaked to the output, and 2) how is the cipher system working; from the pattern of the MI, one can infer which sets of bits undergo the same operations (for more details, please check Section 6.2. in the LeakWatch paper).
We implemented the stream cipher similar to Crypto-1 that works on a half-byte (nibble, 4 bits) and has a 96-bit state. Below shows the brief description of the cipher system:

- The state of the cipher system $s=(s_0,s_1,...,s_{23})$, where each $s_i$ is 4-bit.
- The output of the cipher system $o=f(s)=f_c(f_a(s_4,s_5,s_6,s_7),f_b(s_8,s_9,s_{10},s_{11}),f_b(s_{12},s_{13},s_{14},s_{15}),f_a(s_{16},s_{17},s_{18},s_{19}),f_b(s_{20},s_{21},s_{22},s_{23}))$, where
  - $f_a(a,b,c,d)=((a\lor~b)\oplus~(a\land~d))\oplus~(c\land~((a\oplus~b)\lor~d))$
  - $f_b(a,b,c,d)=((a\land~b)\lor~c)\oplus~((a\oplus~b)\land~(c\lor~d))$
  - $f_c(a,b,c,d,e)=((((a\oplus~b)\oplus~c)\oplus~d)\oplus~e)$
  - $x\land~y:=xy\bmod16$, $x\lor~y:=x^{y+1}\bmod16$, $x\oplus~y:=x+y\bmod16$

We get the ground truth MI from 10K samples; it explicitly shows that first four nibbles of the state are not leaked (MI$=0$) and each of $\{(s_4,s_5,s_6,s_7),(s_{16},s_{17},s_{18},s_{19})\}$ and $\{(s_8,s_9,s_{10},s_{11}),(s_{12},s_{13},s_{14},s_{15}),(s_{20},s_{21},s_{22},s_{23})\}$ undergo the same operations $f_a$ and $f_b$, respectively. We then use subsets of samples of size $n=\rm10,20,50,100,200,500,1000,2000,5000$ to estimate the MI with three estimators: Empirical, Miller, and ChaoSRM. We found that when the sample size is insufficient,

1. Empirical has the largest error,
2. Miller gives false safety that many more nibbles are not leaked when $n<500$, while Empirical and ChaoSRM give the correct result, and
3. the operation pattern is visible in ChaoSRM's estimation when $n\geq200$, while it is only visible in Empirical and Miller's estimation when $n\geq\rm1000$.

This experiment shows that our approach gives safe and accruate MI estimation with a small sample size in a realistic security domain. If it is necessary, we can include the additional experiment for other cipher systems in the camera-ready version.

## Other Comments

- Strengthening the explanation and proof of the underlying theory (R1)

?

- What is the impact of the overestimation? (R1)

The overestimation of the MI can lead to the false sense of insecurity, which may induce unnecessary security countermeasures.

- The statistical techniques can both over or under-estimate the MI (R3)

Indeed, the statistical method can both over or under-estimate the MI. What we described in Section 2.2 is that the Miller's method may underestimate the MI, i.e., giving the false sense of safety, when the sample size is small, which is demonstrated in the experiment.
We will clarify this point in the camera-ready version.

- Does the intuition behind Chao’s estimation, that the number of undetected events is close to the number of detected rare events, hold for <secret,observable> pairs?

Yes. The intuition behind Chao's estimation, that the number of undetected events is close to the number of singleton events, comes from the Chao's inequality (Chao, 1984) that estimates the lower bound of the number of undetected events. Throughout our experiments, we observed it mostly holds for <secret,observable> pairs.