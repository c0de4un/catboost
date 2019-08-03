#include <catboost/libs/model/model_import_interface.h>
#include <catboost/libs/model/model_build_helper.h>
#include <catboost/libs/algo/learn_context.h>
#include <catboost/libs/algo/split.h>
#include <catboost/libs/helpers/progress_helper.h>



namespace NCB{
    class TCPUSnapshotModelLoader : public IModelLoader {
    public:
        TFullModel ReadModel(IInputStream *modelStream) const override {
            Y_UNUSED(modelStream);
            Y_UNREACHABLE();
        }
        TFullModel ReadModel(const TString& snapshotPath) const override {
            CB_ENSURE(NFs::Exists(snapshotPath), "Model file doesn't exist: " << snapshotPath);
            TLearnProgress learnProgress;
            TProfileInfoData profileRestored;
            TProgressHelper(ToString(ETaskType::CPU)).CheckedLoad(snapshotPath, [&](TIFStream* in) {
                learnProgress.Load(in);
                ::Load(in, profileRestored);
            });
            CB_ENSURE(learnProgress.CatFeatures.empty(),
                      "Can't load model trained on dataset with categorical features from snapshot");
            TObliviousTreeBuilder builder(learnProgress.FloatFeatures, learnProgress.CatFeatures,
                                          learnProgress.ApproxDimension);
            TVector<TModelSplit> modelSplits;
            for (ui32 treeId = 0; treeId < learnProgress.TreeStruct.size(); ++treeId) {
                modelSplits.resize(learnProgress.TreeStruct[treeId].Splits.size());
                auto iter = modelSplits.begin();
                for (const TSplit& split : learnProgress.TreeStruct[treeId].Splits) {
                    iter->FloatFeature.FloatFeature = split.FeatureIdx;
                    iter->FloatFeature.Split = learnProgress.FloatFeatures[split.FeatureIdx].Borders[split.BinBorder];
                    ++iter;
                }
                builder.AddTree(modelSplits, learnProgress.LeafValues[treeId],
                                learnProgress.TreeStats[treeId].LeafWeightsSum);
            }
            TFullModel model;
            builder.Build(model.ObliviousTrees.GetMutable());
            model.ModelInfo["params"] = learnProgress.SerializedTrainParams;
            return model;
        }
    };

    TModelLoaderFactory::TRegistrator<TCPUSnapshotModelLoader> CPUSnapshotModelLoaderRegistator(EModelType::CPUSnapshot);
}